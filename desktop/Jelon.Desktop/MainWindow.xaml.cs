using System.Text.Json;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using Jelon.Desktop.Services;

namespace Jelon.Desktop;

public partial class MainWindow : Window
{
    private readonly JelonBridge _bridge = new();

    public MainWindow()
    {
        InitializeComponent();
        _bridge.MessageReceived += OnMessage;
        Loaded += async (_, _) => await StartCoreAsync();
        Closing += async (_, _) => await _bridge.DisposeAsync();
    }

    private async Task StartCoreAsync()
    {
        try
        {
            await _bridge.StartAsync();
            AddActivity("Core bridge started.");
        }
        catch (Exception ex)
        {
            CoreStatusText.Text = "Core unavailable";
            AddActivity("Core start failed: " + ex.Message);
        }
    }

    private async void SendButton_Click(object sender, RoutedEventArgs e) => await SendGoalAsync();

    private async void InputBox_KeyDown(object sender, KeyEventArgs e)
    {
        if (e.Key == Key.Enter && Keyboard.Modifiers == ModifierKeys.Control)
        {
            e.Handled = true;
            await SendGoalAsync();
        }
    }

    private async Task SendGoalAsync()
    {
        var text = InputBox.Text.Trim();
        if (text.Length == 0) return;
        InputBox.Clear();
        AddChat("You", text, false);
        try
        {
            SendButton.IsEnabled = false;
            await _bridge.SendGoalAsync(text);
        }
        catch (Exception ex)
        {
            AddChat("Jelon", "Bridge error: " + ex.Message, true);
        }
        finally { SendButton.IsEnabled = true; }
    }

    private void OnMessage(JsonElement message)
    {
        Dispatcher.Invoke(() =>
        {
            var type = message.TryGetProperty("type", out var t) ? t.GetString() : "unknown";
            var text = message.TryGetProperty("text", out var tx) ? tx.GetString() ?? "" : "";

            switch (type)
            {
                case "status":
                    CoreStatusText.Text = text;
                    AddActivity(text);
                    break;
                case "result":
                    AddChat("Jelon", text, true);
                    AddActivity("Task completed.");
                    break;
                case "error":
                    AddChat("Jelon", text, true);
                    AddActivity("Error: " + text);
                    break;
                case "log":
                    AddActivity(text);
                    break;
            }
        });
    }

    private void AddChat(string author, string text, bool jelon)
    {
        var border = new Border
        {
            Background = jelon ? new SolidColorBrush(Color.FromRgb(17, 24, 33)) : new SolidColorBrush(Color.FromRgb(23, 33, 44)),
            CornerRadius = new CornerRadius(8),
            Padding = new Thickness(14),
            Margin = new Thickness(0, 0, 0, 10)
        };
        var panel = new StackPanel();
        panel.Children.Add(new TextBlock { Text = author.ToUpperInvariant(), FontSize = 10, Foreground = new SolidColorBrush(Color.FromRgb(140, 154, 170)), FontWeight = FontWeights.Bold });
        panel.Children.Add(new TextBlock { Text = text, TextWrapping = TextWrapping.Wrap, Margin = new Thickness(0, 5, 0, 0) });
        border.Child = panel;
        ChatPanel.Children.Add(border);
    }

    private void AddActivity(string text)
    {
        ActivityPanel.Children.Add(new TextBlock
        {
            Text = "• " + text,
            TextWrapping = TextWrapping.Wrap,
            Foreground = new SolidColorBrush(Color.FromRgb(140, 154, 170)),
            Margin = new Thickness(0, 0, 0, 9)
        });
    }
}
