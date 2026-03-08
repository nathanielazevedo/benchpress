namespace InstrumentAgent;

public interface ILogger
{
    void Log(string message);
}

public sealed class ConsoleLogger : ILogger
{
    public void Log(string message) =>
        Console.WriteLine($"[{DateTime.UtcNow:HH:mm:ss}] {message}");
}
