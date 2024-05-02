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

key = ""

# - - - - - - - - - - - - - - - - - - -

class config(object):
  """ Class for storing all account details related to IG Group."""
  username = ""
  password = ""
  api_key = ""
  acc_type = "PROD"
  acc_number = ""

# - - - - - - - - - - - - - - - - - - -

def get_header():
  return header

def get_body():
  return body

def get_username():
  return body["identifier"]

def get_password():
  return body["password"]

def get_key():
  return key
