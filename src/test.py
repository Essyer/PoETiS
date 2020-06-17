test = ['The Learn Python Challenge. Casino.,', 'They bought a car, and a horse', 'Casinoville']


def word_search(doc_list, keyword):
    new_list = []
    for index in range(len(test)):
        if keyword in doc_list[index].lower().replace(",", "").replace(".", "").split():
            new_list.append(index)
        else:
            print(keyword + " not found in: " + str(doc_list[index].lower().strip(".,").split()))
    print(new_list)


word_search(test, 'car')

