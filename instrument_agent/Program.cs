using InstrumentAgent;
using Microsoft.Extensions.Configuration;

var configuration = new ConfigurationBuilder()
    .SetBasePath(AppContext.BaseDirectory)
    .AddJsonFile("appsettings.json", optional: false)
    .AddEnvironmentVariables(prefix: "AGENT_")
    .Build();

var config = configuration.GetSection("Agent").Get<AgentConfig>() ?? new AgentConfig();
var http = new HttpClient();
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
