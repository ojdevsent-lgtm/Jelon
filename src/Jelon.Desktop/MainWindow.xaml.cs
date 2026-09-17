using System.Windows;
namespace Jelon.Desktop;
public partial class MainWindow : Window
{
    public MainWindow() => InitializeComponent();
    private void Run_Click(object sender, RoutedEventArgs e)
    {
        MessageBox.Show($"Agent goal received:\n\n{GoalBox.Text}\n\nThe local agent engine will execute this goal when connected.", "Jelon");
    }
}