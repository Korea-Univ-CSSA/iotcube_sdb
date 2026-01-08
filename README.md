## OSS DB collection code

This is a simplified version of the SDB collection code, to be used for the OSS filtering project.

### DB collection process
osscollector -> preprocessor (-> detector)
- osscollector: Clone OSS repositories, code files undergo normalization / comment removal / hashing.
- preprocessor: OSScollector results are preprocessed & inserted into DB.
- detector: Input SW is analyzed to detect OSS components. (Not used for DB collection)

---

## Running code locally
1. Clone & change working directory to this repository.
2. Add repositories to `/osscollector/sample_c_cpp_add` to include in DB.
3. Run `/osscollector/OSS_Collector_file_C_cpp.py`.
4. Run `/preprocessor/Preprocessor_full_file_c_cpp_1210.py`.
5. Run `/preprocessor/Preprocessor_sqlite.py`.
6. To preprocess input SW, run `hmark_file.py [input_directory]`.
7. To analyze, run `Detector_vers_file.py ./res_hmark_file/[input_hidx]`.
8. Create SBOM file with `create_sbom.py`. (Needs editing)


### SDB 참고 문서
- https://green-raver-0b9.notion.site/SDB-1bdfd561078080849837dbf67a22e0d3?pvs=4
