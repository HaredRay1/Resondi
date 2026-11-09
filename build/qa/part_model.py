"""Q&A on the retrained 4-class lung model (9 Nov 2026). Every number here is from
model-rebuild/results and the checked Edge Impulse build; update them if the model is retrained."""

MODEL = ("THE RETRAINED MODEL (9 Nov): sound labels, patient split", [
 ("“What is your model's accuracy now?”",
  "On 31 patients it has never heard, the rebuilt model scores 33.5 percent balanced accuracy across four "
  "sound patterns, against 25 percent for guessing. It catches about seven in ten breaths with crackles. It "
  "misses most wheezes. That is a weak model, and we say so, but it is the first number we have that measures "
  "something real.\n"
  "It is a screening aid. Every result goes to a practitioner, who confirms, changes or rejects it.", None),

 ("“Your earlier documents said 71 to 84 percent. Why is it lower now?”",
  "Because the earlier number was wrong. The old model was tested on near-copies of audio it had trained on: "
  "the recordings were cut into overlapping clips and shuffled at random, so the same patient's sound sat on "
  "both sides. It was also trained on each patient's diagnosis stamped on every second of their audio, so it "
  "learned to recognise the patient, not the sound.\n"
  "We found that ourselves, rebuilt it properly, and reported the lower number. A team that publishes its own "
  "worse result is a team whose other numbers you can trust.", None),

 ("“What did you change, exactly?”",
  "Three things. First, the labels: every breathing cycle is now labelled with what can be heard in it — crackles, "
  "wheezing, both, or neither — instead of the patient's disease. Second, the split: whole patients go to training "
  "or to testing, never both. Third, the stethoscopes: the dataset was recorded on four different devices, and we "
  "balanced them across training and testing.", None),

 ("“Why do you report balanced accuracy and not plain accuracy?”",
  "Because half of all breaths are normal. A model that always answers “normal” scores about 53 percent plain "
  "accuracy and is useless. Balanced accuracy averages the four sounds equally, so that model scores 25 percent. "
  "On plain accuracy ours is 44 percent, which would look worse than doing nothing. Balanced accuracy is the "
  "fair measure, and we show the per-class results with it.", None),

 ("“Why is it so bad at wheezes?”",
  "Three reasons. Wheezes are the rarer class in the training data. The model listens in one-second windows, "
  "which cut many wheezes short. And the training data comes from European stethoscopes, not ours. We tried "
  "longer windows and they did not help, so the fix is more data, especially recordings from our own device.", None),

 ("“Will it work on Filipino patients recorded with your device?”",
  "We don't know yet, and we found a reason to be careful. In our first attempt, 79 percent of the training audio "
  "came from one stethoscope, and the model failed on patients recorded with the others — it learned the "
  "microphone, not the sound. A change of device alone broke it.\n"
  "That is exactly what the ₱46,000 local recording and labelling line pays for: Filipino patients, recorded on "
  "Resondi, labelled by two clinicians. Until then, every result is reviewed by a practitioner.", None),

 ("“Isn't it dangerous to give health workers a weak model?”",
  "It would be if the model decided anything. It doesn't. It describes a sound, never a disease, and a "
  "practitioner confirms every result before anyone acts on it. The value today is the recording itself — "
  "kept, labelled by site, comparable at the next visit. The model is the part we are still improving, and we "
  "say that openly.", None),

 ("“Is the new model the one running in your app?”",
  "The new model is built, exported and checked: the version that runs in the browser gave the same results on "
  "the test patients as our own testing. Switching the app over is the final step.",
  "Check the app before pitch day. If the new model is live, say “the app now runs it.” If not, keep this answer. "
  "Never say it is live unless it is."),

 ("“How did you test it?”",
  "On ICBHI 2017, the standard public lung-sound database: 920 recordings from 126 patients. 31 of those patients "
  "were kept out completely, 1,051 breathing cycles, and the model was scored on them only once, at the end. We "
  "built it twice, in our own code and in Edge Impulse, and the two agreed.", None),
])
