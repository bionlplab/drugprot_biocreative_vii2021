#! /bin/bash -l

top_dir=$HOME
data_dir=$top_dir/drugprot/large-scale-drugprot
for file in "$data_dir"/mergesent/*.zip; do
    if test -f "$file"; then
#        echo "$file"
        src_file=$(realpath "$file")
        bname=$(basename "$file" .zip)
        dst_file=$data_dir/bert_tag2/${bname}.tsv
        dst_file=$(realpath "$dst_file")
        if test ! -f "$dst_file"; then
#            echo "${src_file}" "${dst_file}"
            sbatch ~/Subjects/drugprot_bcvii/run.sh "${src_file}" "${dst_file}"
        fi
    fi
done