#!/usr/bin/env python3

import pandas

class InternalError(RuntimeError):
    pass


def convert(input_csv, output_xlsx):
    print('Reading input file')
    df = pandas.read_csv(input_csv, index_col=0, dtype={0: str})#, sep=',|;', quotechar='"', **format_specific_args)

    if df.index.name == 'record_id':
        rep_instrument_col = 'redcap_repeat_instrument'
        rep_instance_col = 'redcap_repeat_instance'
    elif df.index.name == 'Record ID':
        rep_instrument_col = 'Repeat Instrument'
        rep_instance_col = 'Repeat Instance'
    else:
        raise InternalError('unrecognized redcap export format, is the input file an original redcap export file?')

    assert all(df[rep_instance_col] != 0)
    df[rep_instrument_col] = df[rep_instrument_col].fillna('Static')
    df[rep_instance_col] = df[rep_instance_col].fillna(0).astype(int)

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

    print('Splitting instruments and repeats')
    acc = {}
    for (instr, rep), rdf in df.groupby([rep_instrument_col, rep_instance_col]):
        assert rep == int(rep)
        rep = int(rep)
        rdf = rdf.drop([rep_instrument_col, rep_instance_col], axis='columns')
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


    print('Merging all pieces')
    first = ('Static', 0)
    keys = sorted(acc.keys())
    keys.remove(first)
    keys = [first] + keys

    sorted_acc = {(k[0], f"Repeat {k[1]}"): acc[k] for k in keys}

    newdf = pandas.concat(sorted_acc, axis='columns')
    newdf.index.name = 'Redcap ID'

    print(f'Writing Excel output, {newdf.shape[0]} rows by {newdf.shape[1]} columns')
    newdf.to_excel(output_xlsx)
    print('DONE')