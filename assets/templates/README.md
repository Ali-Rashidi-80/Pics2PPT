# Pics2PPT templates

Bundled and user-supplied PowerPoint templates for **Hybrid Smart** output.

## Files

| File | Role |
|------|------|
| `Pics2PPT_Default.pptx` | Default cover + theme base used when `output_mode=auto` / `template` and no custom path is set |

## Layout indices

Use **Analyze template** in Settings → PPTX output to dump:

- layout index (0-based)
- placeholder `idx` and type
- shape names

Set `layout_index_grid` in settings (advanced) to force a layout for content slides. If unset, Pics2PPT prefers a layout whose name contains `Blank`.

## Tokens (run-safe)

Place these in text boxes (Selection Pane names optional). Tokens may be split across PowerPoint runs; the fill engine rejoins them safely:

| Token | Meaning |
|-------|---------|
| `{{title}}` | Job / folder name |
| `{{footer}}` | Footer text from Home |
| `{{section}}` | Current section name (when used) |
| `{{job_name}}` | Alias of title |

**Do not** rely on assigning `.text` to styled placeholders in custom tools — Pics2PPT never wipes runs.

## Picture placeholders

If a content layout has `Picture` placeholders, Phase 1+ can fill them via `insert_picture` with `image_fit`: `fit` | `fill` | `native`.

## Security

Templates are validated before load: size limits, zip member caps, path-traversal rejection, OOXML content-types check.

## Custom templates

1. Design in PowerPoint (masters, colors, optional animations).
2. Point Settings → Template file to your `.pptx` or `.potx`.
3. Keep animations on the **template path** only — code path does not invent animations.
