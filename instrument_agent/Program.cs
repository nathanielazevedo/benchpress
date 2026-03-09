using InstrumentAgent;
using Microsoft.Extensions.Configuration;

var configuration = new ConfigurationBuilder()
    .SetBasePath(AppContext.BaseDirectory)
    .AddJsonFile("appsettings.json", optional: false)
    .AddEnvironmentVariables(prefix: "AGENT_")
    .Build();

var config = configuration.GetSection("Agent").Get<AgentConfig>() ?? new AgentConfig();

// Prompt for lab / company IDs if not set in config or env
if (string.IsNullOrWhiteSpace(config.LabId))
{
    Console.Write("Enter Lab ID (UUID from the backend, leave blank to skip): ");
    config = config with { LabId = Console.ReadLine()?.Trim() ?? "" };
}

if (string.IsNullOrWhiteSpace(config.CompanyId))
{
    Console.Write("Enter Company ID (UUID from the backend, leave blank to skip): ");
    config = config with { CompanyId = Console.ReadLine()?.Trim() ?? "" };
}

// Prompt for watch path if not set in config or env
if (string.IsNullOrWhiteSpace(config.WatchPath))
{
    Console.Write("Enter path to watch for instrument output files: ");
    var input = Console.ReadLine()?.Trim() ?? "";

    if (!Directory.Exists(input))
    {
        Console.Error.WriteLine($"Directory not found: '{input}'");
        return;
    }

    config = config with { WatchPath = input };
}

var http   = new HttpClient();
var logger = new ConsoleLogger();

IInstrumentAgent agent = new LabInstrumentAgent(config, http, logger);

using var cts = new CancellationTokenSource();
Console.CancelKeyPress += (_, e) =>
{
    e.Cancel = true;
    cts.Cancel();
};

await agent.StartAsync(cts.Token);
await agent.StopAsync();
