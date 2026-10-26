import qrcode

NAME = "Anton Romaniuk"
GROUP = "IT-32"
EMAIL = "romananukanton343@gmail.com"

print(f"{NAME}, {GROUP}")

text = f"{NAME}, {GROUP}, {EMAIL}"
image = qrcode.make(text)
image.save("contact.png")
print("saved: contact.png")