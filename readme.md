# Poker Table Controller

`Poker Table Controller` is used to automate one's online or offline poker play. It detects and scrapes the poker table, extracting all the useful information from it. It can also interact with the table by folding, betting, checking etc., based on the decision returned through a DLL.

Supports only 6-max cash games at the moment. Multiple instances are automatically ran if multiple tables are identified.

---

## How to use

There are 4 components needed for `Poker Table Controller` to work:
- caches
- a tablemap
- some images to be matched against the table areas scraped (i.e. the images of the cards)
- a DLL that takes the decision and passes it to the controller

---

### Caches

Unzip `caches.7z`.

---

### Tablemap 

A json file named `tablemap.json` that contains all the areas the controller should scrape and interact with. For more info, see [ajecc/tablemap-builder](https://github.com/ajecc/tablemap-builder).

---

### Images

The follwing images are necessary in order for the `Poker Table Controller` to work:
- `identifier.PNG` 
    - an image that identifies that the scraped window belongs to a poker game
- `<card_rank><card_suit>.PNG`
    - images with the cards
    - some valid card image names: `2c.PNG Td.PNG Ac.PNG 9s.PNG`
- `nocard0.PNG` and `nocard1.PNG`
    - indicates that no card is present
- `active.PNG` 
    - indicates that the villain is in the hand, active
- `not_active.PNG`
    - indicates that the villain is not in the hand
    - is compared against `active.PNG`
- `dealer.PNG`
    - indicates that the player is the dealer
- `not_dealer.PNG`
    - indicates that the player is not the dealer
    -is compared against `dealer.PNG`
- `is_hero_turn.PNG`
    - indicates it is the hero's turn
- `is_not_hero_turn.PNG`
    - indicates that is is not hero's turn
    - is compared against `is_hero_turn.PNG`
- `seated.PNG`
    - indicates that the player is seated 
- `not_seated.PNG`
    - indicates that the player is not seated 
    - is compared against `seated.PNG`

Every image must be a `PNG`. An example of how the images should look like can be found in [examples/images](https://github.com/ajecc/tablemap-builder/tree/master/examples/images).

---

### DLL

The DLL must be name `User.dll`.

The DLL must expose 2 functions:
```C
int update_symbols(const char* psymbols);
double process_query(const char* pquery);
```
For more info, see [ajecc/poker-user-dll](https://github.com/ajecc/poker-user-dll).

--- 

### Dependencies

To install the dependencies, run `py -3 -m pip install -r requirements.txt`.

Note that [tesseract](https://github.com/tesseract-ocr/tesseract) also needs to be installed.

---

### Running

Now that the program is all setup, run it with `py -3 main.py`. Note that you might need to run it as an Administrator.

---

## Project Structure

The project is divided in multiple parts:
- `tablemap_grabber.py` 
    - is used for grabbing information about the state of the game 
    - the information is then passed and used by the DLL
    - the decision is made afterwards
    - it uses the `tablemap`
- `card_identifier.py`
    - identifies the cards grabbed
    - might need some tweaking depending on the platform the program is ran against
- `tablemap_clicker.py`
    - moves, clicks and types the right data in the right places
    - used to interact with the game
- `user_dll.py`
    - wrapper for `User.dll`
