all_item_details= {}
for i in range(2):
    
    item_no = 'item : ' + str(i)
    # print(item_no)
    #item_no = dict(item_no)
    per_item_desc_dict = {i:{'Material':'a','Plant':'b','OrderQuantity':'c'}}
    all_item_details.update(per_item_desc_dict)
    # item_dict = dict(zip(item_no,per_item_desc_list))
print(all_item_details)
# print(next(iter(all_item_details)))
print(all_item_details[(list(all_item_details.keys())[0])])
# print(all_item_details[item_no])