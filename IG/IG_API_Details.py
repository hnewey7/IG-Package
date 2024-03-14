'''
Module for storing IG API Key and Account Information.

Created on Tuesday 12th March 2024
@author: Harry New

'''

# - - - - - - - - - - - - - - - - - - -
# IG API Key and Account Input

header = {
  "Content-Type":"application/json; charset=UTF-8",
  "Accept":"application/json; charset=UTF-8",
  "VERSION":"2",
  "X-IG-API-KEY":""
}

body = {
  "identifier": "",
  "password": "",
  "encrytedPassword":False
}

# - - - - - - - - - - - - - - - - - - -

def get_header():
  return header

def get_body():
  return body
