# Prism Stack — ElbowOS

Full-colour Python 3 neon **tower-lite** arcade. Slide a crane-carried slab and drop it onto the stack. Miss the overlap and the floor is lost; nail the alignment and the combo climbs.

Featured account: [https://x.com/ElbowOS](https://x.com/ElbowOS)

## Play

```bash
pip install -r requirements.txt
python3 prism_stack.py
```

Controls: **SPACE** / **K** / **DOWN** drop the moving slab. **R** reset. **ESC** quit.

## Record a 9:16 reel

Needs `ffmpeg` on PATH.

```bash
ELBOWOS_RECORD=1 python3 prism_stack.py
# or
python3 prism_stack.py --record
```

Writes `PRISM_STACK_ElbowOS.mp4` (1080×1920, 15 s, 30 fps, H.264).

## Links

- Reel on Drive: https://drive.google.com/file/d/1FedCJOyjh8WQ3W4amUpL20IgCsalCUm6/view?usp=drivesdk
- ElbowOS: https://x.com/ElbowOS
