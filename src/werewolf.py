
def save_contacts(contacts):
    file = open('contacts.txt','w') 
    for number in contacts:
        file.write(number) 
        file.write('#') 
        file.write(contacts[number])
        file.write('\n') 
    
    file.close()

def get_contacts():
    contacts = {}
    try:
        file = open('contacts.txt','r')
        lines = file.read().split('\n')
        for line in lines:
            content = line.split('#')
            if(len(content)==2):
                contacts[content[0]]=content[1]
            else:
                pass

    except FileNotFoundError:
        pass
    print(contacts)
    return contacts
