
---

# **Jump King Recreation**

Welcome to the **King's Trial**, a fan-made Python project that recreates the thrilling and challenging platformer experience of **Jump King**. This game is built using the **Pygame** library, offering players the same punishing yet addictive gameplay with unique additions and customization options.

---

## **Table of Contents**

- [Features](#features)
- [Installation](#installation)
- [How to Play](#how-to-play)
- [Game Modes](#game-modes)
- [Progress Saving](#progress-saving)
- [Controls](#controls)
- [Assets and Credits](#assets-and-credits)
- [Contributing](#contributing)
- [License](#license)

---

## **Features**

- **Platforming Challenges**: Climb challenging levels full of obstacles, slippery surfaces, trampolines, and hazards.
- **Custom Skins**: Unlock and select skins to customize your character. (https://kevins-moms-house.itch.io/camelot)
- **Dynamic Timer**: Tracks your gameplay time and updates your best time for each run.
- **Coins and Rewards**: Collect coins to unlock special skins and achievements.
- **Health and Fall Damage**: Keep an eye on your health, as falling from great heights can damage your character.
- **Pause and Save System**: Pause the game, save your progress, and continue from where you left off.
- **Developer Mode**: Debug and explore the levels with unlimited movement (for developers and testers).

---

## **Installation**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/PCinkusz/jump-king-recreation.git
   ```
2. **Navigate to the Project Directory**:
   ```bash
   cd jump-king-recreation
   ```
3. **Install Required Dependencies**:
   Ensure you have Python 3.8+ installed. Install the necessary libraries using:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Game**:
   Start the game by running:
   ```bash
   python main.py
   ```

---

## **How to Play**

Your objective is to **ascend to the top** of the levels and hang the kingdom's flag. Be prepared for a challenge as every mistake could send you plummeting back down!

- Avoid hazards, collect coins, and carefully time your jumps to progress through the levels.
- Once at the top, raise the flag to record your final time. You can replay the game to try and beat your best time.

---

## **Game Modes**

- **Single Player**: Take on the challenge of climbing to the top by yourself.
- **Developer Mode**: Toggle developer mode to move freely and explore/debug levels. (Use `U` to enable/disable.)

---

## **Progress Saving**

The game automatically saves your:
- Current level, position, and time when exiting.
- Coins collected and whether skins are unlocked.
- Best completion time.

Saved progress is stored in `progress.json` and `savegame.json` files. You can delete these files manually to reset your progress.

---

## **Controls**

| Action                     | Key                     |
|----------------------------|-------------------------|
| Move Left                  | **A**                  |
| Move Right                 | **D**                  |
| Jump                       | **Space**              |
| Pause                      | **ESC**                |
| Developer Mode (Toggle)    | **U**                  |

---

## **Assets and Credits**

- **Graphics**: Custom sprites for characters, platforms, and backgrounds.
- **Sounds**: Carefully chosen effects for jumps, landings, and interactions.
- **Font**: [Alkhemikal Font](https://www.dafont.com/alkhemikal.font) for in-game text.

---

## **Contributing**

We welcome contributions from the community! If you'd like to contribute:

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature or fix"
   ```
4. Push to your branch:
   ```bash
   git push origin feature-name
   ```
5. Open a Pull Request.

---

## **License**

This project is for **educational purposes** and is distributed under the [MIT License](LICENSE). All rights to the original Jump King game are reserved by the official developers.

---

## **Screenshots**


![Zrzut ekranu 2025-01-17 230640](https://github.com/user-attachments/assets/f61931f3-7bba-40cd-a3b3-db4374749d00)
![Zrzut ekranu 2025-01-17 230647](https://github.com/user-attachments/assets/28fc25fe-aee2-416d-a15d-cc6f7bf2b047)
![entire_map](https://github.com/user-attachments/assets/20d0ae4c-34bb-47d4-9abb-a0596c048c06)




--- 

Enjoy the challenge of King's Trial and strive to beat your best time! 🏆
