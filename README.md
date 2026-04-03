# EMRMacrosOverlay
Adds rudimentary macro function by copying text to clipboard based on a shortcut name. Inspired by EMR dot macros functionality, intended for use in EMRs that lack this basic feature.

# Important Notice
This tool is considered depracated as Canopy is being phased out in favor of Epic Software. Currently I am using [Beeftext](https://github.com/xmichelo/Beeftext/) as it covers most of my needs for text expansion at this time. I am currently using a script based off this code to do chart reviews and concisely generate quick laboratory text lines for easy charting. See: [CanopyTestSuite](https://github.com/ELloydBio/CanopyTestSuite)

## Tutorial
Create basic macros by placing the text to add in a .txt file

  The name of the txt file will be used to call the macro! Choose something descriptive but brief.

Run the python file

Use keyboard shortcut to request data from text file (ctrl + alt + C by default)

Data will automatically be added to clipboard

## Features
Automatic data insertion

  Use "[date]" for today's date 
  
  Use "[time]" for current time
  
  Use "[provider]" for name of medical provider (currently user provided when program opens)
  

## TO DO
Add config file support

Enable custom square bracket fields for data replacement

Add additional graphical config/settings functionality

Tentatively: add web crawler to retrieve pt info from EMRs

## Legal Note
This software in its current state does not handle PHI or PII. In the future, it features may be implemented that enable the software to interface with protected information. It is up to the **end user**  to ensure this information is used responsibly and in accordance with applicable law. No plans currently exist for HPI, or any other information used in this software for that matter, to be uploaded and stored online.
