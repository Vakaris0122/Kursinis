# 1. Įvadas

## a. Kokia yra jūsų programa?
Programa yra Space Shooter žaidimas, sukurtas naudojant Python ir Pygame biblioteką. Žaidime žaidėjas valdo laivą, kuris naršo po kosmosą, vengia asteroidų, šaudo į priešus ir renka power-up'us. Žaidimo tikslas – pereiti per lygius, nugalėti priešus ir pasiekti aukščiausią rezultatą. Žaidime taip pat yra RPG elementų, tokių kaip power-up'ai, greičio stiprinimas ir nesunaikinamumas.

## b. Kaip paleisti programą?
Norėdami paleisti žaidimą:

1. Įdiekite Python (versija 3.x ar aukštesnė) savo kompiuteryje.
2. Įdiekite Pygame biblioteką:
    ```bash
    pip install pygame
    ```
3. Atsisiųskite arba nukopijuokite šaltinio kodą į savo kompiuterį.
4. Atidarykite terminalą arba komandinę eilutę, pereikite į žaidimo katalogą ir paleiskite:
    ```bash
    python space_shooter_game.py
    ```
5. Žaidimo langas atsidarys ir galėsite pradėti žaisti.

## c. Kaip naudoti programą?
Paleidus žaidimą:

### Valdymas:
- Naudokite rodyklių klavišus (aukštyn, žemyn, kairėn, dešinėn), kad judėtumėte su savo laivu.
- Paspauskite SPACE klavišą, kad šaudyti kulkas į priešus.
- Paspauskite P klavišą, kad pauzuotumėte žaidimą.
- Paspauskite ESC klavišą, kad išeitumėte iš žaidimo.

### Power-up'ai:
- Surinkite power-up'us, kad gautumėte laikinas naudas, tokias kaip nesunaikinamumas, greičio stiprinimas ar triple shot.

# 2. Analizė

Žaidėjas gali judėti laivu naudodamasis rodyklių klavišais, o šaudyti kulkas galima paspaudus SPACE klavišą. Žaidimo logika remiasi **Player** klase, kuri valdo judėjimą, šaudymą ir kitus žaidimo elementus. Power-up'ai atsitiktinai atsiranda ekrane, kai žaidėjas juos surenka, aktyvuojami įvairūs privalumai, tokie kaip nesunaikinamumas, greičio stiprinimas arba triple shot. Power-up'ų elgseną valdo **PowerUp** klasė. 

**Priešo AI**: Priešai atsiranda bangomis, juda žemyn ir šaudo į žaidėją. **Enemy** klasė valdo priešų elgseną, o jų šaudymo mechanizmas leidžia priešams šaudyti į žaidėją. **HighScoreManager** klasė seka aukščiausią rezultatą, kurį atnaujina, kai pasiekiamas naujas rekordas.

Žaidimas baigiasi, kai žaidėjo gyvybės pasiekia nulį, ir tada rodomas žaidimo pabaigos ekranas.

# 3. Rezultatai ir Santrauka

Žaidimo mechanika: Žaidėjas gali judėti, šaudyti, rinkti power-up'us ir nugalėti priešus. Laivas, priešų laivai, kulkos ir power-up'ai visi teisingai piešiami ir atnaujinami ekrane.

### Iššūkiai, su kuriais susidūriau:
- Subalansuoti žaidimo sudėtingumą, ypač didinant priešų gyvybes ir greitį, buvo sudėtinga. Reikėjo daug bandymų ir koregavimų.
- Valdyti skirtingas žaidimo būsenas (pvz., žaidimas, pauzė, žaidimo pabaiga) reikalavo didelio dėmesio, kad užtikrintume sklandų pereimą tarp jų.
- Įgyvendinti laikmačius power-up'ams ir užtikrinti, kad jie galioja tik nurodytą laiką, buvo sudėtinga ir reikėjo tiksliai sekti laiką.

## b. Išvados
Programa įgyvendina linksmai žaidžiamą ir interaktyvų žaidimą, kuriame žaidėjas gali valdyti laivą, šaudyti į priešus, rinkti power-up'us ir siekti aukščiausio rezultato.

Pagrindinės žaidimo mechanikos — judėjimas, šaudymas, priešų elgsena, power-up'ai ir įvertinimas — veikia taip, kaip buvo numatyta. Žaidimo sąsaja pateikia realaus laiko informaciją apie žaidėjo gyvybes, taškus ir aukščiausią rezultatą.

## c. Kaip būtų galima išplėsti jūsų programą?
- Įdiegti dviejų žaidėjų režimą, kur žaidėjai galėtų žaisti kartu arba konkuruoti.
- Patobulinti žaidimo grafiką su detalesniais elementais, animacijomis ir fonine muzika, kad žaidimas būtų dar įdomesnis.
- Pridėti daugiau sudėtingų lygių su naujais priešais, kliūtimis ir iššūkiais, kad žaidimas būtų dar įdomesnis.
- Sukurti internetinę lyderių lentą, kad žaidėjai galėtų palyginti savo rezultatus su kitais pasauliniu mastu.
- Sukurti priešus su sudėtingesniais elgesio modeliais, pvz., įvairiais šaudymo modeliais arba strateginiu judėjimu.
