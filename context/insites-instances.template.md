# My Insites Instances

*This file is gitignored - personal to your machine. Copy this template to `context/insites-instances.md` and fill in the projects you work on.*

Instance URLs and environment details are stored in the Teamwork "Claude" custom item for each project. Use the combinate skill to look them up. Store your API keys in `.env` using the naming convention below.

## Key Naming Convention

```
COMBINATE_KEY_[CLIENT_TLA]_[PROJECT_TLA]_[ENV]=your_key_here
```

ENV values: `PRD` (production), `STG` (staging), `UAT`, `DEV`

## Projects I Work On

List the projects you're actively developing on. Look up TLA values and URLs from the Teamwork "Claude" custom item.

| Client | Client TLA | Project TLA | Environments |
|--------|-----------|------------|-------------|
| e.g. British Chamber of Commerce | BCC | WEB | PRD, STG, UAT |

## Notes

- Get your API key values from Shane or Erin
- Add the corresponding `COMBINATE_KEY_*` entries to your `.env` file
- Your personal developer key (`INSITES_CLI_KEY`) works across all instances
