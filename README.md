# music-tools

Collection of handy digital-musicology tools for dataset preparation, computing etc.

Right now it can:
1. Get pitch bounds of your dataset
2. Normalize dataset to C4 major/A5 minor/atonal
3. Distribute computation of any script on all data into multiple cores
4. Correct midifiles so that note_off(or ons with velocity==0) come before note_ons (helps with writing tools to convert midi to a ML friendly format)
