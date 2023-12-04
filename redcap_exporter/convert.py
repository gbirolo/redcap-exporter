#!/usr/bin/env python3

import pandas

def convert(input_csv, output_xlsx):
    df = pandas.read_csv(input_csv, index_col=0, dtype={0: str})

    assert all(df['Repeat Instance'] != 0)
    df['Repeat Instrument'] = df['Repeat Instrument'].fillna('Static')
    df['Repeat Instance'] = df['Repeat Instance'].fillna(0).astype(int)

    # detect duplicate columns, redcap repeats column names (for instance "Complete?" for each instrument)
    likely_dups = df.columns[df.columns.str.endswith('.1')]
    dedup_cols = {}
    for dup_col in likely_dups:
        orig_col = dup_col[:-2]
        if orig_col in df.columns:
            # real duplicate (very very likely)
            for i in range(1, 1000):
                dup_col_i = orig_col + f'.{i}'
                if dup_col_i in df.columns:
                    dedup_cols[dup_col_i] = orig_col
                else:
                    break

    acc = {}
    for (instr, rep), rdf in df.groupby(['Repeat Instrument', 'Repeat Instance']):
        assert rep == int(rep)
        rep = int(rep)
        rdf = rdf.drop(['Repeat Instrument', 'Repeat Instance'], axis='columns')
        rdf = rdf.dropna(axis='columns', how='all')
        rdf = rdf.rename(columns=dedup_cols)

        # rename columns with repeat
        if False and rep > 0:
            rdf.columns = rdf.columns + f'_REP{rep}'
            #rdf = rdf.set_index('Repeat Instru')

        dups = rdf.index.duplicated().sum()
        if dups > 0:
            print(f'{dups} duplicates in rep {rep} of {instr}:')
            print(rdf.loc[rdf.index.duplicated(keep=False)])

        #acc.append(rdf)
        acc[(instr, rep)] = rdf


    first = ('Static', 0)
    keys = sorted(acc.keys())
    keys.remove(first)
    keys = [first] + keys

    sorted_acc = {(k[0], f"Repeat {k[1]}"): acc[k] for k in keys}

    newdf = pandas.concat(sorted_acc, axis='columns')
    newdf.index.name = 'Redcap ID'
    newdf.to_excel(output_xlsx)