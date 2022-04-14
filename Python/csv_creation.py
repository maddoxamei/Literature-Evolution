#for the words 
statfanfics = stats_fiction.toDF()
statfanfics.write.option('header'=True).option('delimiter',',').csv("/home/krodriguez/dcproj1/onlybook")
#repeat for other stats

#for the dialogue stats 
List_cols = ['min_cl','max_cl','ave_cl','vae_cl','ave_dl','ave_ds','ave_wsr','prp_dpara']
list_rows = stats_books
with open('books.csv','w') as csvfile:
    write = csv.writer(csvfile)
    write.writerow(list_cols)
    write.writerows(list_rows)

#repeat with same col names for fanfic stats