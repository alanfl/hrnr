import re

# Open a file: file
file = open('log', mode='r')
 
# read all lines at once
data = file.read()

# Extract Recording ID

# Get a new connection.
# Get the first message for initialization. recording, logdir:/replay_logdb/rec_1, pid:3744, connection times:1

start = 0
pattern = re.compile(r"Get a new connection.(?:\r\n|\r|\n)Get the first message for initialization. recording, logdir:/replay_logdb/rec_(.*), pid:.*(?:\r\n|\r|\n)")
m = pattern.search(data, start)
rid = m.group(1)
print("Recording ID: " + rid)
start = m.end(0)
# print(start)

# extract GetKeyboardMapping Request
keystr = ''

# request  opcode:101  sequence:1081  size:8
# ----------------------
#     1: 101,
#     unused 1
#     2: 2,0,
#     1: 8, (keystart)
#     1: 248,
#     unused 2
# ----------------------
pattern = re.compile(r"request  opcode:101  sequence.*(?:\r\n|\r|\n)(?:.*(?:\r\n|\r|\n)){4}(.*)(?:\r\n|\r|\n)")
m = pattern.search(data, 0)
keystart = int(m.group(1).split(':')[1].split(',')[0])
# print(keystart)

# current size is 4096
# reply  opcode:101  sequence:1081  size:6976 outputLength:1620
# ----------------------
#     1: 1,
#     1: 7, (syms per keycode)
#     2: 57,4,
#     4: 200,6,0,0,
#     unused 24
#     remaining 6944: 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,27,255, ...
# ----------------------
pattern = re.compile(r"reply  opcode:101  sequence.*(?:\r\n|\r|\n)(?:.*(?:\r\n|\r|\n)){2}(.*)(?:\r\n|\r|\n)(?:.*(?:\r\n|\r|\n)){3}(.*)(?:\r\n|\r|\n)")
m = pattern.search(data, 0)

l = m.group(1).split(':')[1].split(',')
symperkey = int(l[0]);
# print(symperkey);
# X window has 4 groups per key
grpperkey = 4;

l = m.group(2).split(':')[1].split(',')
del l[-1]
keymap = list(map(lambda curr: int(curr), l))
# print(keymap)

# event opcode:2 is for X Window KeyPress event

# event   opcode:2  sequence:1080  size:32
# 2,12,56,4,168,137,108,4,85,1,0,0,93,0,64,4,218,0,64,4,161,0,131,0,94,0,31,0,0,0,1,0,

# 12 is the keycode
# last [-3] [-4] are keyboard modifiers (shift/control/... 8 of them) and groups(4 of them)
# Modifier: Shift, Lock, Control, Mod1, Mod2, Mod3, Mod4, Mod5

start = 0
while True:
  # extract KeyPress Event
  pattern = re.compile(r"event   opcode:2  sequence.*(?:\r\n|\r|\n)(.*)(?:\r\n|\r|\n)")
  m = pattern.search(data, start)
  if m is None:
    break

  # 2,12,56,4,168,137,108,4,85,1,0,0,93,0,64,4,218,0,64,4,161,0,131,0,94,0,31,0,0,0,1,0,
  # 12 - keycode which need to be converted to key symbol 
  l = m.group(1).split(',')
  # print(l)
  del l[-1]

  # get keycode
  keycode = int(l[1])
  # print(keycode)

  # ...,0,0,1,0
  # [-3] and [-4] together 16 bits for modifier and group
  # bits 0-7 (least significant 8 bits for modifiers, shift,lock,control,...)
  # bits 13-14 (2 bits for group #)
  keymod = int(l[-3])
  # print(keymod)
  # none - 0, shift - 1, others - ?
  
  keygrp = int(l[-4])
  # print(keygrp)
  # seems always 0

  # lookup the key symbol from keycode and modifier
  keysym = keymap[(keycode-keystart)* symperkey * grpperkey + keymod + keygrp]
  keystr += chr(keysym)
  # print(chr(keysym))

  # search next from the end of current match
  # m.end(0) return the end index of the current match
  start = m.end(0)
  # print(start)

print("User Input: " + keystr)
