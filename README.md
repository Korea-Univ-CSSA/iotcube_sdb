### SDB 참고 문서
- https://green-raver-0b9.notion.site/SDB-1bdfd561078080849837dbf67a22e0d3?pvs=4


## OSS DB collection code
osscollector -> preprocessor (-> detector)


### osscollector
- add_gitclone: Used to clone OSS repositories.
- OSS_Collector: Code files of OSS undergo normalization / comment removal / hashing.


### preprocessor
- Preprocessor_full_file: Hash values & version information of OSS code are preprocessed & inserted into DB.
- Preprocessor_sqlite: DB organized into SQL format.


### detector (not used for DB collection)
- hmark_file: Input SW of Hatbom is analyzed by file granularity.
- Detector_vers_file: File hashes of input SW are compared with OSS DB to find OSS dependencies. 
- create_sbom: Analysis result is organized into SBOM format.

