# Roastly

## Description

This is a flask app for personal use recording all of my coffee roasts on my FreshRoast 540.

The roast page should mirror the interface on the roaster, the user should adjust the temperature, fan, and power to match the adjustments made on the roaster.

## To Do

- DB Changes:
    - elapsed time to int
    - temperature to int
    - settings to include F | Cd
- Add shades | images of roasts to the `end_roast` template to help the user determine which level they just roasted
- Nav bar improvements
    - Increase the size of the text in the navbar
    - Right align the buttons in nav bar
    - Change font on buttons
- Template improvements
    - move icon credit text to actual page footer
    - look at other websites and decide how to align the body content
    - add images to the actions 'add a new bean' 'start a new roast'
- Settings page
    - create a settings page which allows you to set default values for the temperature, fan, and power
    - fix the roast diary to pull these values
- Bean page
    - create a bean page to show how many times a bean was roasted to a certain level (bar chart of roast levels and counts)
    - add tips for what time and temp this bean typically hits first crack
- Roast page
    - Add stats on how many times this roast level has been used
        - and specifically for this bean
    - Did the fan go as low as usual?
    - Did the cracks happen around the same time frame?
    - When was the first adjustment made?
    - When did the temperature start to level off?
- Client refactor
    - use an interface objects that contain each of our components
    - clicking a button calls the interface to delagate to that component
- Hosting
- Generate shareable link / QR code to roast