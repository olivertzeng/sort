> [!NOTE]
> A specific step by step on how to process the whole file

Initial file
```csv

Header
1, a witness,
explanation,
example #1,
2, an apple,
explanation,
example #1,
example #2,
3, the world,
4, cat,
meow,
5, (this刂is) a happy ending,
 6, (it's刂a) hat,
it's a hat

```

Cleaning
```csv

1, a witness,
explanation,
example #1,
2, an apple,
explanation,
example #1,
example #2,
3, the world,
4, cat,
meow,
5, (this刂is) a happy ending,
6, (it's刂a) hat,
it's a hat

```

Grouping
```csv
 a witness,甭explanation,甭example #1,
 an apple,甭explanation,甭example #1,甭example #2,
 the world,
 cat,甭meow,
 (this刂is) a happy ending,
 (it's刂a) hat,甭it's a hat
```

Blocking
n = 0
```csv
a witness,甭explanation,甭example #1,
an apple,甭explanation,甭example #1,甭example #2,
the world,
cat,甭meow,
(this刂is) a happy ending,
(it's刂a) hat,甭it's a hat
```

n = 1
```csv
a witness,甭explanation,甭example #1,
an apple,甭explanation,甭example #1,甭example #2,
the world,
峀 cat,甭meow,
(this刂is) a happy ending,
(it's刂a) hat,甭it's a hat
```

n = 2(all the 2nd word are not blocked, break)
```csv
峀 a witness,甭explanation,甭example #1,
峀 an apple,甭explanation,甭example #1,甭example #2,
峀 the world
峀 峀 cat,甭meow,
(this刂is) a happy ending,
峀 (it's刂a) hat,甭it's a hat
```

Sorting
```csv
峀  an apple,甭explanation,甭example #1,甭example #2,
峀 峀  cat,甭meow,
 (this刂is) a happy ending,
峀  (it's刂a) hat,甭it's a hat
峀  a witness,甭explanation,甭example #1,
峀  the world,
```

Labeling
```csv
1,峀  an apple,甭explanation,甭example #1,甭example #2,
2,峀 峀  cat,甭meow,
3, (this刂is) a happy ending,
4,峀  (it's刂a) hat,甭it's a hat
5,峀  a witness,甭explanation,甭example #1,
6,峀  the world,
```

Output
```csv

Header

1, an apple,
explanation,
example #1,
example #2,
2, cat,
meow,
3, (this is) a happy ending,
4, (it's a) hat,
it's a hat
5, a witness,
explanation,
example #1,
6, the world,
```
