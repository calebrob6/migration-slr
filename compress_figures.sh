#!/bin/bash

for f in output/figures/*.tiff; do
    fn=$(basename $f)
    if tiffcp -c lzw "output/figures/$fn" "output/figures_compressed/$fn"; then
        #touch -r "$f" "$out" && mv "$out" "$f";
        echo $fn
    else
        echo "ERROR with $f";
    fi;
done

#convert -density 300 -compress lzw -flatten Fig1.eps Fig1.tiff
#convert -density 300 -compress lzw Fig2.pdf Fig2.tiff
#convert -density 300 -compress lzw Fig3.pdf Fig3.tiff
