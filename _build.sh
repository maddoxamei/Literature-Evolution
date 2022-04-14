#!/bin/sh

set -ev

Rscript -e "bookdown::render_book('R/01-Introduction.Rmd', 'bookdown::gitbook')"
#Rscript -e "bookdown::render_book('R/01-Introduction.Rmd', 'bookdown::pdf_book')"
#Rscript -e "bookdown::render_book('R/01-Introduction.Rmd', 'bookdown::epub_book')"