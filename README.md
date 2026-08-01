# warrior-brain-plugins

Claude Code plugin marketplace configuration.

## Marketplaces

This repository registers the [`wshobson/agents`](https://github.com/wshobson/agents)
repository as a known plugin marketplace named `claude-code-workflows`.

The configuration lives in [`.claude/settings.json`](.claude/settings.json) so it
is shared with anyone who works in this repository:

```json
{
  "extraKnownMarketplaces": {
    "claude-code-workflows": {
      "source": {
        "source": "github",
        "repo": "wshobson/agents"
      }
    }
  }
}
```

## Applying the configuration to your user config

The project settings above are picked up automatically when Claude Code runs in
this repository. To register the same marketplace in your personal Claude Code
configuration, run:

```bash
claude config set extraKnownMarketplaces.claude-code-workflows.source.source github
claude config set extraKnownMarketplaces.claude-code-workflows.source.repo wshobson/agents
```

Once registered, the marketplace can be browsed and its plugins installed with
the `/plugin` command.
