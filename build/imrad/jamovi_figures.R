# Resondi IMRaD: statistical figures and tables produced with jamovi's own analysis engine (R package jmv).
#
# Every analysis here is the same one jamovi runs from its menus, so a reader can reproduce each result
# by opening the CSV files in jamovi (steps in model-rebuild/results/stats/JAMOVI-STEPS.md, section 11).
#
# Inputs  : model-rebuild/results/stats/jamovi_cv_folds.csv, jamovi_cv_patients.csv, jamovi_cv_cycles.csv
#           (written by model-rebuild/scripts/export_jamovi_cv.py)
# Outputs : figures/j1_cv_folds.png, j2_cv_patients.png, j3_cv_confusion_*.png
#           build/imrad/jamovi-output.txt (every jamovi table, as text)
#
# Run:  "C:\Program Files\R\R-4.6.2\bin\Rscript.exe" build\imrad\jamovi_figures.R   (from the Resondi folder)

.libPaths(file.path(Sys.getenv("LOCALAPPDATA"), "R/win-library/4.6"))
suppressPackageStartupMessages(library(jmv))

args <- commandArgs(trailingOnly = FALSE)
here <- dirname(normalizePath(sub("^--file=", "", args[grep("^--file=", args)])))
root <- normalizePath(file.path(here, "..", ".."))
stats <- file.path(root, "model-rebuild", "results", "stats")
figs <- file.path(root, "figures")
log <- file.path(here, "jamovi-output.txt")

sink(log)
cat("jamovi (jmv", as.character(packageVersion("jmv")), ") output for the Resondi IMRaD\n")
cat("Generated", format(Sys.time(), "%Y-%m-%d %H:%M"), "\n\n")

save_plot <- function(img, file, w = 1400, h = 1000) {
  ragg::agg_png(file.path(figs, file), width = w, height = h, res = 220)
  print(img)
  invisible(dev.off())
}

# 1. Fold-level balanced accuracy: paired-samples t-test + Wilcoxon (Analyses > T-Tests > Paired Samples)
folds <- read.csv(file.path(stats, "jamovi_cv_folds.csv"), check.names = FALSE)
names(folds)[names(folds) == "balacc_mfcc"] <- "MFCC network"
names(folds)[names(folds) == "balacc_fusion"] <- "Fusion network"
cat("== 1. Five folds: balanced accuracy (%), paired samples\n")
r1 <- ttestPS(folds, pairs = list(list(i1 = "MFCC network", i2 = "Fusion network")),
              wilcoxon = TRUE, meanDiff = TRUE, ci = TRUE, effectSize = TRUE, desc = TRUE, plots = TRUE)
print(r1)
save_plot(r1$plots[[1]], "j1_cv_folds.png")

# 2. Per-patient share of cycles correct: paired samples, 126 patients
pats <- read.csv(file.path(stats, "jamovi_cv_patients.csv"), check.names = FALSE)
names(pats)[names(pats) == "pct_correct_mfcc"] <- "MFCC network"
names(pats)[names(pats) == "pct_correct_fusion"] <- "Fusion network"
cat("\n== 2. 126 patients: % of each patient's cycles classified correctly, paired samples\n")
r2 <- ttestPS(pats, pairs = list(list(i1 = "MFCC network", i2 = "Fusion network")),
              wilcoxon = TRUE, meanDiff = TRUE, ci = TRUE, effectSize = TRUE, desc = TRUE, plots = TRUE)
print(r2)
save_plot(r2$plots[[1]], "j2_cv_patients.png")

# 3. Cycle-level confusion matrices and McNemar (Analyses > Frequencies)
cyc <- read.csv(file.path(stats, "jamovi_cv_cycles.csv"), check.names = FALSE)
lev <- c("Crackles", "Healthy", "Wheezing", "Wheezing with Crackles")
cyc$`True class` <- factor(cyc$true_label, levels = lev)
cyc$`Predicted (MFCC)` <- factor(cyc$pred_mfcc, levels = lev)
cyc$`Predicted (fusion)` <- factor(cyc$pred_fusion, levels = lev)
cyc$`MFCC correct` <- factor(ifelse(cyc$correct_mfcc == 1, "Correct", "Wrong"), levels = c("Correct", "Wrong"))
cyc$`Fusion correct` <- factor(ifelse(cyc$correct_fusion == 1, "Correct", "Wrong"), levels = c("Correct", "Wrong"))

for (m in c("MFCC", "fusion")) {
  col <- paste0("Predicted (", m, ")")
  cat("\n== 3. Cross-validation contingency table, ", m, " network (row % = recall)\n", sep = "")
  r3 <- do.call(contTables, list(data = cyc, rows = "True class", cols = col, pcRow = TRUE, chiSq = FALSE,
                   barplot = TRUE, yaxis = "ypc", yaxisPc = "row_pc", xaxis = "xrows", bartype = "dodge"))
  print(r3$freqs)
  # Plot copy with the long class name wrapped, so the axis labels do not overlap.
  short <- cyc
  levels(short$`True class`)[4] <- "Wheezing with\nCrackles"
  levels(short[[col]])[4] <- "Wheezing with\nCrackles"
  r3p <- do.call(contTables, list(data = short, rows = "True class", cols = col, pcRow = TRUE, chiSq = FALSE,
                   barplot = TRUE, yaxis = "ypc", yaxisPc = "row_pc", xaxis = "xrows", bartype = "dodge"))
  save_plot(r3p$barplot, paste0("j3_cv_confusion_", tolower(m), ".png"), w = 1900, h = 1050)
}

cat("\n== 4. McNemar: the same 6,898 cycles, MFCC vs fusion correct/wrong (Frequencies > Paired Samples)\n")
r4 <- contTablesPaired(cyc, rows = "MFCC correct", cols = "Fusion correct", exact = TRUE, pcRow = FALSE)
print(r4)

# 5. Field agreement of the ORIGINAL model: 6 of 15 vs 25% chance (Frequencies > 2 Outcomes)
field <- data.frame(Agreement = factor(c(rep("Match", 6), rep("No match", 9)), levels = c("Match", "No match")))
cat("\n== 5. Field agreement of the original model, binomial test against 0.25\n")
r5 <- propTest2(field, vars = "Agreement", testValue = 0.25, hypothesis = "greater", ci = TRUE)
print(r5)
sink()
cat("wrote figures and", log, "\n")
