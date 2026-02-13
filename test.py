def main_app():
    print("Tervetuloa pelaamaan totuuslabyrinttia! \n Vastaa kysymyksiin kirjoittamalla joko 1 tai 2.")

    
    options = [
         (20, 40), 
         (10, 30), 
         (60, 79), 
         (24, 54)]
    
    score = 0
    for i, option_pair in enumerate(options):
        question = f"Kumpi näistä numeroista on suurempi? Kysymys {i + 1}"
        print(question)
        print(f"Vaihtoehto 1: {option_pair[0]} \nVaihtoehto 2: {option_pair[1]}")

        result = option_pair[0] > option_pair[1]
        if result == True:
             correctanswer = 1
        else:
             correctanswer = 2  
        try: 
            userchoice = int(input("1 or 2: "))
            if userchoice == correctanswer:
                print(f"Vastasit vaihtoehto {userchoice}: {option_pair[userchoice-1]}, joka on oikein! Jatketaan seuraavaan kysymykseen...")
                score+=1
                print(f"Your score: {score}")
            else:
                print(f"Vastasit vaihtoehto {userchoice}: {option_pair[userchoice-1]}, joka on väärin. Oikea vastaus oli vaihtoehto {correctanswer}: {option_pair[correctanswer-1]}")
                print(f"Your score: {score}")
                exit()


        except Exception as e:
            print(f"Virhe tapahtuu: Vastaa kysymyksiin kirjoittamalla joko 1 tai 2! {e}")
            exit()


main_app()