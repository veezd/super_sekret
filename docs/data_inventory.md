# Raw data inventory (auto: scripts/inspect_raw.py)

header=None -> row numbers are raw. Find real header row before loading.


## Basen 2025.csv (846 KB)

### sheet `csv enc=cp1250 sep=';'` shape=(8760, 7) non-null/col=[8760, 8760, 8760, 8760, 8760, 8760, 8760]
```
              0                         1                       2                 3            4                  5               6
0   Nr platnika  Nr punktu poboru energii          Rodzaj energii    Data i godzina       Strefa  Wartosc[kWh/kvar]  Kompletnosc[%]
1      60168852    PPE:590322429402049120  energia czynna pobrana  01.01.2025 01:00  Reszta dnia              75,33             100
2      60168852    PPE:590322429402049120  energia czynna pobrana  01.01.2025 02:00  Reszta dnia             75,792             100
3      60168852    PPE:590322429402049120  energia czynna pobrana  01.01.2025 03:00  Reszta dnia             96,114             100
4      60168852    PPE:590322429402049120  energia czynna pobrana  01.01.2025 04:00  Reszta dnia             95,322             100
5      60168852    PPE:590322429402049120  energia czynna pobrana  01.01.2025 05:00  Reszta dnia             94,986             100
6      60168852    PPE:590322429402049120  energia czynna pobrana  01.01.2025 06:00  Reszta dnia             95,904             100
7      60168852    PPE:590322429402049120  energia czynna pobrana  01.01.2025 07:00  Reszta dnia             96,738             100
8      60168852    PPE:590322429402049120  energia czynna pobrana  01.01.2025 08:00  Reszta dnia             97,116             100
9      60168852    PPE:590322429402049120  energia czynna pobrana  01.01.2025 09:00  Reszta dnia             95,532             100
10     60168852    PPE:590322429402049120  energia czynna pobrana  01.01.2025 10:00  Reszta dnia             90,012             100
11     60168852    PPE:590322429402049120  energia czynna pobrana  01.01.2025 11:00  Reszta dnia             79,062             100
...
             0                       1                       2                 3            4      5    6
8757  60168852  PPE:590322429402049120  energia czynna pobrana  31.12.2025 22:00  Reszta dnia   88,2  100
8758  60168852  PPE:590322429402049120  energia czynna pobrana  31.12.2025 23:00  Reszta dnia  87,66  100
8759  60168852  PPE:590322429402049120  energia czynna pobrana  01.01.2026 00:00  Reszta dnia  87,96  100
```

## Dane D-17 2025.xls (6311 KB)

### sheet `Sheet1` shape=(35076, 9) non-null/col=[35070, 35032, 35003, 0, 1, 35031, 35001, 0, 1]
```
                                                                                                                                          0    1    2    3        4    5    6    7    8
0                                                                                                                                       NaN  NaN  NaN  NaN  Tabular  NaN  NaN  NaN  NaN
1                                                                                                                                       NaN  NaN  NaN  NaN      NaN  NaN  NaN  NaN  NaN
2                                                                                                                                       NaN  NaN  NaN  NaN      NaN  NaN  NaN  NaN  NaN
3                                                                                                                                       NaN  NaN  NaN  NaN      NaN  NaN  NaN  NaN  NaN
4                                                                                2025-01-01 00:00:00 - 2026-01-01 00:00:00 (Serwer lokalny)  NaN  NaN  NaN      NaN  NaN  NaN  NaN  NaN
5                                                                                                                                       NaN  NaN  NaN  NaN      NaN  NaN  NaN  NaN  NaN
6                                                                                                        Informacej wymagające twojej uwagi  NaN  NaN  NaN      NaN  NaN  NaN  NaN  NaN
7            Znaleziono braki pomiędzy '2025-04-12 00:00:00' i '2025-04-12 00:15:00': RG_D17_nn.ZAS1_PM5500  Energia Czynna Pobrana  (kWh).  NaN  NaN  NaN      NaN  NaN  NaN  NaN  NaN
8            Znaleziono braki pomiędzy '2025-05-25 19:15:00' i '2025-05-25 19:30:00': RG_D17_nn.ZAS1_PM5500  Energia Czynna Pobrana  (kWh).  NaN  NaN  NaN      NaN  NaN  NaN  NaN  NaN
9            Znaleziono braki pomiędzy '2025-07-18 05:30:00' i '2025-07-18 05:45:00': RG_D17_nn.ZAS1_PM5500  Energia Czynna Pobrana  (kWh).  NaN  NaN  NaN      NaN  NaN  NaN  NaN  NaN
10           Znaleziono braki pomiędzy '2025-08-01 08:45:00' i '2025-08-01 10:15:00': RG_D17_nn.ZAS1_PM5500  Energia Czynna Pobrana  (kWh).  NaN  NaN  NaN      NaN  NaN  NaN  NaN  NaN
11  Znaleziono braki pomiędzy '2025-02-05 00:30:00' i '2025-02-05 01:00:00': RG_D17_nn.ZAS1_PM5500  Moc Czynna Uśred. (met. Blokowa)  (kW).  NaN  NaN  NaN      NaN  NaN  NaN  NaN  NaN
...
                                              0            1                  2    3    4            5                  6    7    8
35073                       2025-12-31 23:45:00  1699805.694  35.55683135986328  NaN  NaN  3375561.264  65.43753814697266  NaN  NaN
35074                       2026-01-01 00:00:00    1699815.5  42.76267623901367  NaN  NaN  3375577.174  63.58906173706055  NaN  NaN
35075  ID: 822d9ba9-b877-43c5-85ba-53128ac2f60f          NaN                NaN  NaN  NaN          NaN                NaN  NaN  NaN
```

## MS_AGH_energia_ele_i_cieplna_2023-2025.xlsx (56 KB)

### sheet `zużycie ciepła 23r.` shape=(52, 29) non-null/col=[0, 0, 0, 47, 42, 41, 41, 43, 43, 45, 45, 45, 44, 44, 42, 42, 0, 0, 47, 0]
```
     0    1    2             3                                      4    5    6    7    8    9   ...   19    20   21   22    23   24   25   26   27   28
0   NaN  NaN  NaN           NaN                                    NaN  NaN  NaN  NaN  NaN  NaN  ...  NaN   NaN  NaN  NaN   NaN  NaN  NaN  NaN  NaN  NaN
1   NaN  NaN  NaN           NaN                                    NaN  NaN  NaN  NaN  NaN  NaN  ...  NaN   NaN  NaN  NaN   NaN  NaN  NaN  NaN  NaN  NaN
2   NaN  NaN  NaN           NaN                                    NaN  NaN  NaN  NaN  NaN  NaN  ...  NaN   NaN  NaN  NaN   NaN  NaN  NaN  NaN  NaN  NaN
3   NaN  NaN  NaN           NaN  Zużycie energii cieplnej w 2023r w GJ  NaN  NaN  NaN  NaN  NaN  ...  NaN   NaN  NaN  NaN   NaN  NaN  NaN  NaN  NaN  NaN
4   NaN  NaN  NaN           NaN                                    NaN  NaN  NaN  NaN  NaN  NaN  ...  NaN   NaN  NaN  NaN   NaN  NaN  NaN  NaN  NaN  NaN
5   NaN  NaN  NaN           m-c                                      1    2    3    4    5    6  ...  NaN  c.w.  NaN  NaN  c.o.  NaN   CT  NaN  NaN  NaN
6   NaN  NaN  NaN     DS.-1 c.o                                    391  422  349  235  120    0  ...  NaN   NaN  NaN  NaN  2372  NaN  NaN  NaN  NaN  NaN
7   NaN  NaN  NaN     DS.-1 c.w                                    172  146  172  160  115  138  ...  NaN  1552  NaN  NaN   NaN  NaN  NaN  NaN  NaN  NaN
8   NaN  NaN  NaN    DS.-2 c.o.                                    372  418  371  279  165   33  ...  NaN   NaN  NaN  NaN  2684  NaN  NaN  NaN  NaN  NaN
9   NaN  NaN  NaN     DS.-2 c.w                                    214  177  255  202  176  113  ...  NaN  1969  NaN  NaN   NaN  NaN  NaN  NaN  NaN  NaN
10  NaN  NaN  NaN    DS.-3 c.o.                                    NaN  NaN  NaN  159  126    0  ...  NaN   NaN  NaN  NaN  1110  NaN  NaN  NaN  NaN  NaN
11  NaN  NaN  NaN  DS.-3 c.w.u.                                    NaN  NaN  NaN  123  149  147  ...  NaN  1157  NaN  NaN   NaN  NaN  NaN  NaN  NaN  NaN
...
     0    1    2          3     4     5     6     7     8     9   ...   19       20   21   22       23   24   25   26    27    28
49  NaN  NaN  NaN   ALFA c.o   720   760   632   434   227     0  ...  NaN      NaN  NaN  NaN     4311  NaN  NaN  NaN   NaN   NaN
50  NaN  NaN  NaN  Alfa c.w.   245   204   288   251   233   211  ...  NaN     2687  NaN  NaN      NaN  NaN  NaN  NaN   NaN   NaN
51  NaN  NaN  NaN      RAZEM  6332  6433  6380  4667  3178  1564  ...  NaN  19167.2  NaN  NaN  23191.2  NaN  373  677  1399  1799
```

### sheet `energia elektryczna 23r.` shape=(52, 18) non-null/col=[0, 0, 47, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 21, 26, 4]
```
     0    1                                           2      3      4      5       6      7      8      9      10     11     12     13     14          15        16           17
0   NaN  NaN                                         NaN    NaN    NaN    NaN     NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN         NaN       NaN          NaN
1   NaN  NaN                                         NaN    NaN    NaN    NaN     NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN         NaN       NaN          NaN
2   NaN  NaN                                         NaN    NaN    NaN    NaN     NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN         NaN       NaN          NaN
3   NaN  NaN  Zużycie energii elektrycznej w 2023r w kWh    NaN    NaN    NaN     NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN         NaN       NaN          NaN
4   NaN  NaN                                         NaN      I     II    III  IV        V       VI    VII   VIII     IX      X     XI    XII  suma dzień  suma noc  RAZEM D + N
5   NaN  NaN                                     DS.-1 D  51420  40350  43035   25590  32070  20289  12885  12180  14190  40125  41835  20670      354639       NaN          NaN
6   NaN  NaN                                      DS.-1N  28935  23640  24195   15435  19830  12750   9315   8385   9360  21960  23130  36330         NaN    233265          NaN
7   NaN  NaN                                     DS.-2 D  23505  16470  23745   16755  17880  13815  12165  11340  12390  21525  22125  19335      211050       NaN          NaN
8   NaN  NaN                                     DS.-2 N   4174   9660  12795    9495  10410   8340   7590   7005   7860  11505  12120  10650         NaN    111604          NaN
9   NaN  NaN                                     DS.-3 D  31860  24360  29370   21540  25200  25260  22170  22260  19110  28620  30900  30000      310650       NaN          NaN
10  NaN  NaN                                      DS.-3N  14910  14400  16410   13170  15720  15990  14580  14280  12030  16080  16980  16500         NaN    181050          NaN
11  NaN  NaN                                     DS.-4 D  13200   9660  12240    9360  10980   7260   7020   6660   6660  11580  10740  10920      116280       NaN          NaN
...
     0    1                2      3      4      5      6      7      8      9      10     11     12     13     14   15   16       17
49  NaN  NaN       RAZEM ALFA  50330  46376  51934  42952  50790  44884  38946  44342  30449  50369  50997  47936  NaN  NaN   550305
50  NaN  NaN              NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN  NaN  NaN      NaN
51  NaN  NaN  Zużycie łącznie    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN  NaN  NaN  4782523
```

### sheet `zużycie ciepła 24r.` shape=(53, 26) non-null/col=[0, 0, 0, 45, 41, 36, 39, 34, 39, 41, 40, 40, 40, 39, 41, 42, 0, 0, 44, 0]
```
     0    1    2           3                                      4    5    6    7    8    9   ...   16   17     18   19    20   21   22    23   24   25
0   NaN  NaN  NaN         NaN                                    NaN  NaN  NaN  NaN  NaN  NaN  ...  NaN  NaN    NaN  NaN   NaN  NaN  NaN   NaN  NaN  NaN
1   NaN  NaN  NaN         NaN                                    NaN  NaN  NaN  NaN  NaN  NaN  ...  NaN  NaN    NaN  NaN   NaN  NaN  NaN   NaN  NaN  NaN
2   NaN  NaN  NaN         NaN                                    NaN  NaN  NaN  NaN  NaN  NaN  ...  NaN  NaN    NaN  NaN   NaN  NaN  NaN   NaN  NaN  NaN
3   NaN  NaN  NaN         NaN  Zużycie energii cieplnej w 2024r w GJ  NaN  NaN  NaN  NaN  NaN  ...  NaN  NaN    NaN  NaN   NaN  NaN  NaN   NaN  NaN  NaN
4   NaN  NaN  NaN         NaN                                    NaN  NaN  NaN  NaN  NaN  NaN  ...  NaN  NaN    NaN  NaN   NaN  NaN  NaN   NaN  NaN  NaN
5   NaN  NaN  NaN         m-c                                      1    2    3    4    5    6  ...  NaN  NaN  RAZEM  NaN  c.o.  NaN  NaN  c.w.  NaN   CT
6   NaN  NaN  NaN   DS.-1 c.o                                    521  301  284  180   80    0  ...  NaN  NaN   2450  NaN  2450  NaN  NaN   NaN  NaN  NaN
7   NaN  NaN  NaN   DS.-1 c.w                                    222  141  197  165  152  106  ...  NaN  NaN   1643  NaN   NaN  NaN  NaN  1643  NaN  NaN
8   NaN  NaN  NaN  DS.-2 c.o.                                    512  361  321  NaN   76    0  ...  NaN  NaN   2179  NaN  2179  NaN  NaN   NaN  NaN  NaN
9   NaN  NaN  NaN   DS.-2 c.w                                    244  182  235  NaN  183  124  ...  NaN  NaN   1845  NaN   NaN  NaN  NaN  1845  NaN  NaN
10  NaN  NaN  NaN   DS.-3 c.o                                    512  319  293  186   52    0  ...  NaN  NaN   2535  NaN  2535  NaN  NaN   NaN  NaN  NaN
11  NaN  NaN  NaN   DS.-3 c.w                                    244  178  240  202  192  125  ...  NaN  NaN   1879  NaN   NaN  NaN  NaN  1879  NaN  NaN
...
     0    1    2                       3    4    5    6    7    8    9   ...   16   17   18   19   20   21   22   23   24   25
50  NaN  NaN  NaN                     NaN  NaN  NaN  NaN  NaN  NaN  NaN  ...  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN
51  NaN  NaN  NaN  Ds.10 C.T- nowy odczyt  NaN  NaN  NaN  NaN  NaN  NaN  ...  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN
52  NaN  NaN  NaN                     NaN  NaN  NaN  NaN  NaN  NaN       ...  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN
```

### sheet `energi elektryczna 24r.` shape=(52, 18) non-null/col=[0, 0, 47, 41, 41, 41, 41, 41, 41, 41, 41, 41, 41, 41, 41, 21, 21, 4]
```
     0    1                                           2      3      4      5       6      7      8      9      10     11     12     13     14          15        16           17
0   NaN  NaN                                         NaN    NaN    NaN    NaN     NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN         NaN       NaN          NaN
1   NaN  NaN                                         NaN    NaN    NaN    NaN     NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN         NaN       NaN          NaN
2   NaN  NaN                                         NaN    NaN    NaN    NaN     NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN         NaN       NaN          NaN
3   NaN  NaN  Zużycie energii elektrycznej w 2024r w kWh    NaN    NaN    NaN     NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN         NaN       NaN          NaN
4   NaN  NaN                                         NaN      I     II    III  IV        V       VI    VII   VIII     IX      X     XI    XII  suma dzień  suma noc  RAZEM D + N
5   NaN  NaN                                     DS.-1 D  47265  28230  33495   33675  29895  30495  11955   9480  13425  34665  32610  30660      335850       NaN          NaN
6   NaN  NaN                                      DS.-1N  26640  16680  17775   18705  17220  17820   7710   5940   8040  18135  17385  17010         NaN    189060          NaN
7   NaN  NaN                                     DS.-2 D  30030  27870  26520   27780  25890  25650  21870  18930  20430  28320  27510  29100      309900       NaN          NaN
8   NaN  NaN                                     DS.-2 N  16950  16080  15090   16830  15720  15240  13650  12060  12990  15240  15060  16710         NaN    181620          NaN
9   NaN  NaN                                     DS.-3 D  33120  28920  28920   29280  26610  25530  14790  11310  12630  24990  25080  24720      285900       NaN          NaN
10  NaN  NaN                                      DS.-3N  18690  16830  16200   17850  16470  16230   9390   7410   7950  13230  13500  13740         NaN    167490          NaN
11  NaN  NaN                                     DS.-4 D  11940  10740  10680   11040  10800  10140   7560   4860   6360  10560  11160  11640      117480       NaN          NaN
...
     0    1                2      3      4      5      6      7      8      9    10     11     12     13     14   15   16       17
49  NaN  NaN       RAZEM ALFA  53810  39600  46120  42750  59030  53740  76220    0  23660  71430  31720  63930  NaN  NaN   562010
50  NaN  NaN              NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN  NaN    NaN    NaN    NaN    NaN  NaN  NaN      NaN
51  NaN  NaN  Zużycie łącznie    NaN    NaN    NaN    NaN    NaN    NaN    NaN  NaN    NaN    NaN    NaN    NaN  NaN  NaN  4966625
```

### sheet `zużycie ciepła 25r.` shape=(55, 26) non-null/col=[0, 0, 0, 47, 46, 45, 45, 45, 45, 46, 45, 45, 45, 45, 45, 45, 0, 0, 46, 0]
```
     0    1    2           3                                      4    5      6      7      8      9   ...   16   17                  18   19      20   21   22      23   24   25
0   NaN  NaN  NaN         NaN                                    NaN  NaN    NaN    NaN    NaN    NaN  ...  NaN  NaN                 NaN  NaN     NaN  NaN  NaN     NaN  NaN  NaN
1   NaN  NaN  NaN         NaN                                    NaN  NaN    NaN    NaN    NaN    NaN  ...  NaN  NaN                 NaN  NaN     NaN  NaN  NaN     NaN  NaN  NaN
2   NaN  NaN  NaN         NaN                                    NaN  NaN    NaN    NaN    NaN    NaN  ...  NaN  NaN                 NaN  NaN     NaN  NaN  NaN     NaN  NaN  NaN
3   NaN  NaN  NaN         NaN  Zużycie energii cieplnej w 2025r w GJ  NaN    NaN    NaN    NaN    NaN  ...  NaN  NaN                 NaN  NaN     NaN  NaN  NaN     NaN  NaN  NaN
4   NaN  NaN  NaN         NaN                                    NaN  NaN    NaN    NaN    NaN    NaN  ...  NaN  NaN                 NaN  NaN     NaN  NaN  NaN     NaN  NaN  NaN
5   NaN  NaN  NaN         m-c                                      1    2      3      4      5      6  ...  NaN  NaN               RAZEM  NaN    c.o.  NaN  NaN    c.w.  NaN   CT
6   NaN  NaN  NaN   DS.-1 c.o                                    449  477  319.4    180  154.9   21.6  ...  NaN  NaN              2769.1  NaN  2769.1  NaN  NaN     NaN  NaN  NaN
7   NaN  NaN  NaN   DS.-1 c.w                                  176.6  140  208.1  165.2  169.6  140.6  ...  NaN  NaN  1632.1000000000004  NaN     NaN  NaN  NaN  1632.1  NaN  NaN
8   NaN  NaN  NaN  DS.-2 c.o.                                  448.2  337  327.3  189.1  167.6   30.5  ...  NaN  NaN                2666  NaN    2666  NaN  NaN     NaN  NaN  NaN
9   NaN  NaN  NaN   DS.-2 c.w                                  220.3  186  253.5  193.6  188.8  161.4  ...  NaN  NaN              2027.5  NaN     NaN  NaN  NaN  2027.5  NaN  NaN
10  NaN  NaN  NaN   DS.-3 c.o                                    454  459  331.7  188.4  153.3   10.7  ...  NaN  NaN              2727.6  NaN  2727.6  NaN  NaN     NaN  NaN  NaN
11  NaN  NaN  NaN   DS.-3 c.w                                  211.1  179  243.4  184.7  192.3  168.5  ...  NaN  NaN              2083.9  NaN     NaN  NaN  NaN  2083.9  NaN  NaN
...
     0    1    2                       3    4    5    6    7    8    9   ...   16   17   18   19   20   21   22   23   24   25
52  NaN  NaN  NaN                     NaN  NaN  NaN  NaN  NaN  NaN  NaN  ...  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN
53  NaN  NaN  NaN  Ds.10 C.T- nowy odczyt  NaN  NaN  NaN  NaN  NaN  NaN  ...  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN
54  NaN  NaN  NaN                     NaN  NaN  NaN  NaN  NaN  NaN       ...  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN
```

### sheet `energia elektryczna 25r.` shape=(52, 18) non-null/col=[0, 0, 47, 41, 41, 41, 41, 41, 41, 41, 41, 41, 41, 40, 40, 2, 2, 1]
```
     0    1                                           2      3      4      5       6      7      8      9      10     11     12     13     14          15        16           17
0   NaN  NaN                                         NaN    NaN    NaN    NaN     NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN         NaN       NaN          NaN
1   NaN  NaN                                         NaN    NaN    NaN    NaN     NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN         NaN       NaN          NaN
2   NaN  NaN                                         NaN    NaN    NaN    NaN     NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN         NaN       NaN          NaN
3   NaN  NaN  Zużycie energii elektrycznej w 2025r w kWh    NaN    NaN    NaN     NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN    NaN         NaN       NaN          NaN
4   NaN  NaN                                         NaN      I     II    III  IV        V       VI    VII   VIII     IX      X     XI    XII  suma dzień  suma noc  RAZEM D + N
5   NaN  NaN                                     DS.-1 D  13046  34267  26731   35339  28141  33376  24168   6330   7903  23589  26100  26700         NaN       NaN          NaN
6   NaN  NaN                                      DS.-1N   7522  18708  14861   19462  16924  19692  14606   4457   5291  13100  14505  15060         NaN       NaN          NaN
7   NaN  NaN                                     DS.-2 D  11875  27760  23642   30031  24715  27397  22249  17741  17880  24771  26280  29070         NaN       NaN          NaN
8   NaN  NaN                                     DS.-2 N   6873  15194  13377   16956  14793  16061  13533  11330  11470  14155  14730  16680         NaN       NaN          NaN
9   NaN  NaN                                     DS.-3 D  10570  26260  21026   25115  20486  22951  19473  16480  15715  18283  24300  24900         NaN       NaN          NaN
10  NaN  NaN                                      DS.-3N   6136  14845  11660   14165  12500  14095  12152  10183   9769   3927  13260  13950         NaN       NaN          NaN
11  NaN  NaN                                     DS.-4 D   5036  11852   8738   10666   9104  10411   8452   5338   5362   8053   9780  10560         NaN       NaN          NaN
...
     0    1                2      3      4      5      6      7      8    9      10     11   12   13   14   15   16   17
49  NaN  NaN       RAZEM ALFA  41620  48060  52920  49400  40310  45800    0  80930  30010    0  NaN  NaN  NaN  NaN  NaN
50  NaN  NaN              NaN    NaN    NaN    NaN    NaN    NaN    NaN  NaN    NaN    NaN  NaN  NaN  NaN  NaN  NaN  NaN
51  NaN  NaN  Zużycie łącznie    NaN    NaN    NaN    NaN    NaN    NaN  NaN    NaN    NaN  NaN  NaN  NaN  NaN  NaN  NaN
```

## Nowa Hala Sportowa 2025.xls (5827 KB)

### sheet `Sheet1` shape=(35043, 6) non-null/col=[35031, 35029, 35025, 0, 2, 35030]
```
                                                             0    1    2    3        4    5
0                                                          NaN  NaN  NaN  NaN  Tabular  NaN
1                                                          NaN  NaN  NaN  NaN      NaN  NaN
2                                                          NaN  NaN  NaN  NaN      NaN  NaN
3                                                          NaN  NaN  NaN  NaN      NaN  NaN
4   2025-01-01 00:00:00 - 2026-01-01 00:00:00 (Serwer lokalny)  NaN  NaN  NaN      NaN  NaN
5                                                          NaN  NaN  NaN  NaN      NaN  NaN
6                                                          NaN  NaN  NaN  NaN      NaN  NaN
7                                                          NaN  NaN  NaN  NaN      NaN  NaN
8                                                          NaN  NaN  NaN  NaN      NaN  NaN
9                                                          NaN  NaN  NaN  NaN      NaN  NaN
10                                                         NaN  NaN  NaN  NaN      NaN  NaN
11                                                         NaN  NaN  NaN  NaN      NaN  NaN
...
                                              0                   1                    2    3    4                   5
35040                       2025-12-31 23:45:00  24.616884231567383  0.16760219633579254  NaN  NaN  24.784486427903175
35041                       2026-01-01 00:00:00  23.836288452148438  0.16663122177124023  NaN  NaN  24.002919673919678
35042  ID: e2a96d5e-9989-419e-8aeb-2315ef767675                 NaN                  NaN  NaN  NaN                 NaN
```

## Profil mocy Hala Sportowa 2025.xls (3415 KB)

### sheet `Sheet1` shape=(35040, 5) non-null/col=[35034, 35028, 0, 0, 1]
```
                                                                                                                                        0                                                            1    2    3        4
0                                                                                                                                     NaN                                                          NaN  NaN  NaN  Tabular
1                                                                                                                                     NaN                                                          NaN  NaN  NaN      NaN
2                                                                                                                                     NaN                                                          NaN  NaN  NaN      NaN
3                                                                                                                                     NaN                                                          NaN  NaN  NaN      NaN
4                                                                              2025-01-01 00:00:00 - 2026-01-01 00:00:00 (Serwer lokalny)                                                          NaN  NaN  NaN      NaN
5                                                                                                                                     NaN                                                          NaN  NaN  NaN      NaN
6                                                                                                      Informacej wymagające twojej uwagi                                                          NaN  NaN  NaN      NaN
7   Znaleziono braki pomiędzy '2025-07-04 10:00:00' i '2025-07-04 12:15:00': Nowa_Hala_Sportowa.RSN1_PM1_PM8240  Moc Czynna Uśred.  (kW).                                                          NaN  NaN  NaN      NaN
8   Znaleziono braki pomiędzy '2025-07-04 12:30:00' i '2025-07-04 13:00:00': Nowa_Hala_Sportowa.RSN1_PM1_PM8240  Moc Czynna Uśred.  (kW).                                                          NaN  NaN  NaN      NaN
9   Znaleziono braki pomiędzy '2025-07-04 14:00:00' i '2025-07-04 14:30:00': Nowa_Hala_Sportowa.RSN1_PM1_PM8240  Moc Czynna Uśred.  (kW).                                                          NaN  NaN  NaN      NaN
10                                                                                                                                    NaN                                                          NaN  NaN  NaN      NaN
11                                                                                                                       Znacznik czasowy  Nowa_Hala_Sportowa.RSN1_PM1_PM8240\nMoc Czynna Uśred.\n(kW)  NaN  NaN      NaN
...
                                              0                  1    2    3    4
35037                       2025-12-31 23:45:00  98.46753692626953  NaN  NaN  NaN
35038                       2026-01-01 00:00:00  95.34515380859375  NaN  NaN  NaN
35039  ID: 9f938bba-be55-4d62-9830-94906131976a                NaN  NaN  NaN  NaN
```

## Profil poboru - AGH MS.xlsx (495 KB)

### sheet `AGH - DS18` shape=(8709, 4) non-null/col=[8708, 8708, 8708, 8708]
```
                      0                 1                              2                                 3
0                   NaN               NaN                            NaN                               NaN
1           Data i czas  Moc czynna\n[kW]  Moc bierna indukcyjna\n[kVar]  Moc bierna pojemnościowa\n[kVar]
2   2026-07-04 00:15:00              28.8                              0                                 0
3   2026-07-04 00:30:00              26.4                            2.4                                 0
4   2026-07-04 00:45:00              28.8                              0                                 0
5   2026-07-04 01:00:00              26.4                            2.4                                 0
6   2026-07-04 01:15:00              26.4                              0                                 0
7   2026-07-04 01:30:00                24                            2.4                                 0
8   2026-07-04 01:45:00                24                              0                                 0
9   2026-07-04 02:00:00                24                              0                                 0
10  2026-07-04 02:15:00                24                            2.4                                 0
11  2026-07-04 02:30:00                24                              0                                 0
...
                        0     1    2  3
8706  2026-10-02 16:15:00    24    0  0
8707  2026-10-02 16:30:00  21.6  2.4  0
8708  2026-10-02 16:45:00    24    0  0
```

### sheet `AGH _ Akropol 50088752` shape=(8738, 4) non-null/col=[8737, 8705, 8705, 8705]
```
                      0                 1                              2                                 3
0                   NaN               NaN                            NaN                               NaN
1           Data i czas  Moc czynna\n[kW]  Moc bierna indukcyjna\n[kVar]  Moc bierna pojemnościowa\n[kVar]
2   2026-07-04 00:15:00              31.2                              0                                 0
3   2026-07-04 00:30:00              33.6                              0                                 0
4   2026-07-04 00:45:00              31.2                              0                                 0
5   2026-07-04 01:00:00              31.2                              0                                 0
6   2026-07-04 01:15:00              31.2                              0                               2.4
7   2026-07-04 01:30:00              28.8                              0                                 0
8   2026-07-04 01:45:00              26.4                              0                                 0
9   2026-07-04 02:00:00              28.8                              0                                 0
10  2026-07-04 02:15:00                24                              0                                 0
11  2026-07-04 02:30:00                24                            2.4                                 0
...
                        0    1    2    3
8735  2026-10-02 23:30:00  NaN  NaN  NaN
8736  2026-10-02 23:45:00  NaN  NaN  NaN
8737  2026-10-03 00:00:00  NaN  NaN  NaN
```

### sheet `AGH Akropol 50088740` shape=(8707, 4) non-null/col=[8706, 8706, 8706, 8706]
```
                      0                 1                              2                                 3
0                   NaN               NaN                            NaN                               NaN
1           Data i czas  Moc czynna\n[kW]  Moc bierna indukcyjna\n[kVar]  Moc bierna pojemnościowa\n[kVar]
2   2026-07-04 00:15:00              21.6                              0                                 0
3   2026-07-04 00:30:00              21.6                            2.4                                 0
4   2026-07-04 00:45:00              19.2                              0                                 0
5   2026-07-04 01:00:00              19.2                              0                                 0
6   2026-07-04 01:15:00              16.8                              0                                 0
7   2026-07-04 01:30:00              16.8                              0                                 0
8   2026-07-04 01:45:00              16.8                              0                                 0
9   2026-07-04 02:00:00              16.8                              0                               2.4
10  2026-07-04 02:15:00              14.4                              0                                 0
11  2026-07-04 02:30:00              16.8                              0                                 0
...
                        0     1    2  3
8704  2026-10-02 15:45:00  43.2    0  0
8705  2026-10-02 16:00:00  40.8    0  0
8706  2026-10-02 16:15:00  45.6  2.4  0
```