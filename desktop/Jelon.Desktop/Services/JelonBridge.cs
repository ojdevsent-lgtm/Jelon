using System.Diagnostics;
using System.Text;
using System.Text.Json;

namespace Jelon.Desktop.Services;

public sealed class JelonBridge : IAsyncDisposable
{
    private Process? _process;
    private readonly SemaphoreSlim _writeLock = new(1, 1);
    public event Action<JsonElement>? MessageReceived;

    public bool IsRunning => _process is { HasExited: false };

    public async Task StartAsync(string python = "python")
    {
        if (IsRunning) return;

        var psi = new ProcessStartInfo
        {
            FileName = python,
            Arguments = "-m engine.desktop_server",
            WorkingDirectory = FindRepoRoot(),
            UseShellExecute = false,
            RedirectStandardInput = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true,
            StandardOutputEncoding = Encoding.UTF8,
            StandardErrorEncoding = Encoding.UTF8
        };

        _process = new Process { StartInfo = psi, EnableRaisingEvents = true };
        _process.Start();

        _ = Task.Run(ReadLoopAsync);
        _ = Task.Run(async () =>
        {
            while (_process is { HasExited: false })
            {
                var line = await _process.StandardError.ReadLineAsync();
                if (line is null) break;
                MessageReceived?.Invoke(JsonSerializer.SerializeToElement(new { type = "log", text = line }));
            }
        });

        await SendAsync(new { type = "status" });
    }

    public async Task SendGoalAsync(string text)
        => await SendAsync(new { type = "goal", text });

    public async Task SendAsync(object message)
    {
        if (!IsRunning) throw new InvalidOperationException("Jelon core is not running.");
        var json = JsonSerializer.Serialize(message);
        await _writeLock.WaitAsync();
        try
        {
            await _process!.StandardInput.WriteLineAsync(json);
            await _process.StandardInput.FlushAsync();
        }
        finally { _writeLock.Release(); }
    }

    private async Task ReadLoopAsync()
    {
        if (_process is null) return;
        while (!_process.HasExited)
        {
            var line = await _process.StandardOutput.ReadLineAsync();
            if (string.IsNullOrWhiteSpace(line)) continue;
            try
            {
                using var doc = JsonDocument.Parse(line);
                MessageReceived?.Invoke(doc.RootElement.Clone());
            }
            catch (JsonException)
            {
                MessageReceived?.Invoke(JsonSerializer.SerializeToElement(new { type = "log", text = line }));
            }
        }
    }

    private static string FindRepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null)
        {
            if (File.Exists(Path.Combine(dir.FullName, "README.md")) &&
                Directory.Exists(Path.Combine(dir.FullName, "engine")))
                return dir.FullName;
            dir = dir.Parent;
        }
        return Environment.CurrentDirectory;
    }

    public async ValueTask DisposeAsync()
    {
        try
        {
            if (IsRunning) await SendAsync(new { type = "shutdown" });
        }
        catch { }
        if (_process is { HasExited: false }) _process.Kill(true);
        _process?.Dispose();
        _writeLock.Dispose();
    }
}
