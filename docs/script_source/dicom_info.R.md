```python 
library(tidyverse)

latest_factors <- c("MPRAGE",
                    "ORIG MPRAGE",
                    "Cube T2",
                    "Filtered Cube T2",
                    "ORIG Cube T2",
                    "SD Tones1",
                    "SD Tones2",
                    "Story Math1",
                    "Story Math2",  
                    "Story Math3",
                    "Rest1",
                    "Rest2",
                    "SE Map1 PE1",
                    "pepolar=1 SE Map1 PE2")

v0.1_factors <- c("Ax FSPGR 3D",
                  "fMRI tones run1",
                  "fMRI tones run2",
                  "fMRI tones run3",
                  "fMRI run1 story-math 1",
                  "fMRI run2 story-math 2",
                  "fMRI run3 story-math 3",
                  "fMRI rest run1",
                  "fMRI rest run2")

ecp_factors <- c("MPRAGE",
                "Cube T2",
                "Rest 1 PE1",
                "Rest 2 PE2",
                "Sem PE1 r1",
                "Sem PE2 r2",
                "SE Map PE1",
                "pepolar=1 SE Map PE2",
                "Lang PE1 r1",
                "Lang PE2 r2",
                "Rest 3 PE1",
                "Rest 4 PE2",
                "Filtered Cube T2")
                    

init_df <- tibble(dicom_files = Sys.glob("sub-*/dicominfo.tsv"))                    

# init_df <- tibble(dicom_files = list.files(pattern = "sub-[[:digit:]]{5}s01")) %>%
#   mutate(dicom_files = file.path(dicom_files, "dicominfo.tsv"))

all_data <- init_df %>%
  mutate(data = map(dicom_files, read_delim, 
                    delim = "\t", 
                    col_types = cols(PatientID = col_character()))) %>%
  unnest(data) 

print_subject_info <- function(subject, factors) {
    results <- all_data %>%
      filter(str_detect(dicom_files, subject), SeriesDescription %in% factors) %>%
      mutate(SeriesDescription = ordered(SeriesDescription, factors)) %>%
      select(SeriesNumber, SeriesDescription, TotalFiles, PatientID, AcquisitionDate) %>%
      arrange(SeriesDescription, SeriesNumber) %>%
      print(n = Inf)
}
 

```