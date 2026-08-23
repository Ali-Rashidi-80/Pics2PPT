# Pics2PPT plugins

Drop optional Python plugins here (`%USERPROFILE%\.pics2ppt\plugins\`).

Enable **Load plugins** in Settings → PPTX features.

## Example `hello.py`

```python
def register(registry):
    def after_build(path, job, settings, **kwargs):
        print("built", path, job.name)

    registry.register("after_build", after_build)
```

## Hooks

| Hook | When |
|------|------|
| `before_build` | Before HybridEngine generates slides |
| `after_build` | After PPTX is written |
| `after_validate` | After validator runs (if build report enabled) |

Plugin failures are isolated and recorded as warnings — they never abort a build.
