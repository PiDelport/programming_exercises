## Programming exercises

Files in this repository will be various exercises I have done, mostly stored here for my own reference. Don't expect anything earth-shattering. Some of these were from interview code challenges.

I do tend to use a lot of functions. That's mostly keeping in practice for larger projects.

---

### What's here?
- FizzBuzz.py - What you expect, but other conditions can be added easily and word order can be changed if desired.
- port_check.py - This was a code challenge for an interview. It demonstrates a use case for Python threads. It could be re-implemented with multiprocessing but there would have to be some rewriting as the threads do updates of a global dictionary (relatively safe in this use case.)
- file_duplicate_detection.py - Single-thread duplicate file finder that returns a dict with duplicates and any that are hardlinks.
- file_duplicate_detection_parallel.py - Like above but using multiprocessing some parts that can be done in parallel. Roughly halved the time needed on my little desktop.
