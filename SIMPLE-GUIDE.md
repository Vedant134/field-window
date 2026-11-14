# Field Window: our project in plain words

## 1. What does NASA want?
A tool that uses NASA information about Earth to help farmers compare changes to the crops they grow over time. It should explain the benefits, problems, and things we still do not know.

## 2. What are we building?
A simple website that asks: “Could I grow something useful between harvesting one crop and planting the next?”
It compares three choices: keep the farmer’s current approach, add one researched planting option, or add another. Extra plants may help protect the ground, but they also need water, time, and work.

## 3. What should the first page show?
A Merced example already filled in, with three short questions:
- What do you currently do during the break?
- When is the field available, and when must the next crop start?
- Can you water an extra crop: rainfall only, some irrigation, or unsure?
Then one button: “Compare my options.” Save answers so the farmer does not repeat them.
For this first version, the location is fixed. There is no map or automatic farm detection.

## 4. Which resources do we use?
| Resource | What it gives us | How we use it |
| --- | --- | --- |
| NASA POWER | Past daily rainfall and temperatures | Our code downloads the records and calculates conditions during the selected months. |
| UC agricultural references | Information about crop timing and management | We read the guidance and store the supported checks in a small reference file. These are not extra weather APIs. |
| Farmer’s answers | Dates, existing practice, and water category | We use them to define the comparison and flag missing information. |
Other satellite datasets and soil maps are left out of this version.

## 5. What happens after the button is pressed?
1. Read the farmer’s dates.
2. Find that same calendar window in each historical year.
3. Add up rainfall and count relevant temperature events.
4. Compare the window and conditions with documented planting requirements.
5. Show what fits, what raises concerns, and what needs checking.
NASA tells us what the weather was. Agricultural guidance tells us what plants need. Our app compares those pieces.

## 6. Where is the data science?
- Data cleaning: check missing records and units.
- Historical time-series analysis: compare weather across past seasons.
- Requirement checks: test dates and weather against documented guidance.
- Sensitivity analysis: change a date or assumption and show what changes.
No machine learning or training is needed. We are analyzing history, not predicting next year.

## 7. What does the app produce?
Three comparison cards, a simple crop calendar, and a rainfall chart.
Each card answers: Does it fit the dates? What might it help with? What water and work does it need? What is still unknown?
A “Why?” button shows the evidence. The farmer can print or save the comparison.

## 8. What works now, and what is unfinished?
Working: real NASA POWER data, historical charts, dates and water inputs, a calendar, and three cards. The current example compares existing management with oats for cover and oats for animal feed—two uses of the same plant.
Unfinished: confirming an actual local crop sequence and checking the alternatives with agricultural expertise. We have not proved enough growing time, water, or compatibility with the next crop. We do not predict profit, yield, or measured soil improvement.

## 9. How do we explain it to a judge?
“We use NASA weather history and agricultural guidance to help a farmer compare what to do between two crops. We show the choices, the tradeoffs, and the missing information in one place.”

## Sources
- NASA POWER: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- UC SAREP oat profile: https://sarep.ucdavis.edu/covercrop/oat
- UC ANR crop-rotation guidance: https://ucanr.edu/sites/default/files/2024-09/402186.pdf
- Challenge: https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/
