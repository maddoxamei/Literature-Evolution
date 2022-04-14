#!/bin/sh

set -ev

Rscript -e "bookdown::render_book('R/01-introduction.Rmd', 'bookdown::gitbook')"
#Rscript -e "bookdown::render_book('R/01-introduction.Rmd', 'bookdown::pdf_book')"
#Rscript -e "bookdown::render_book('R/01-introduction.Rmd', 'bookdown::epub_book')"