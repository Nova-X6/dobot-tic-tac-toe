# Dobot robotic arm tic-tac-toe

Recovered academic project combining minimax game logic, Dobot Magician motion commands, board-state tracking, a GUI, and Arduino infrared sensing experiments.

## Useful starting files

| File under original-code | What it contains | Recovery finding |
| --- | --- | --- |
| `final final.py` | Dobot connection, suction pick-and-place sequence, minimax, Tkinter interface | Strong starting point for the GUI and real-device branch; opens COM3 at module level |
| `virtual test of final final.py` | Virtual game variant | Inspect for software-only demonstration; not executed during recovery |
| `final final v2.py` | Minimax, serial sensor read, mock Dobot | Uses MockDobot, so this version is not evidence of real robot motion |
| `final final v3.py` | Serial sensor read and pick-and-place calls | Refers to device without initializing it; incomplete as archived |
| `xo algo updates.py` | Alternate minimax and robot movement integration | IR sensor reader is a dummy implementation; motion sequence needs end-effector review |
| `xo algo v4.py` and `xo minimax algo.py` | Earlier game-logic variants | Useful development history, not selected as a final integrated application |

`arduino/ir_code_arduino/ir_code_arduino.ino` reads nine sensor pins, A0 through A8, and sends comma-separated values at 9600 baud. A compatible board and matching wiring are required. Python variants that send an `R` request and use a one-second timeout need reconciliation with the sketch, which streams readings with a roughly three-second delay and does not process that request.

The original robotics-lab presentation is retained in the local recovery collection and is not included in this source repository.

## Validation

All recovered Python files passed syntax parsing. The pure minimax functions extracted from `final final.py` passed immediate-win, forced-block, draw-detection, and board-preservation checks. Top-level initialization, GUI code, serial connections, and motion commands were not executed.

## Restoration needs

Choose and reconcile a single hardware or virtual entry point, configure ports and board/cube coordinates for the actual setup, verify player-turn and terminal-game handling, and test sensor timing. The archived motion variants use four robot cubes and require review of game length and cube inventory. The presence of an import or function is not proof that the full hardware workflow was completed.

Third-party packages referenced include pydobot and pyserial; the GUI uses Tkinter. No dependency versions were recovered or installed.
