#!/usr/local/bin/python3

import csv
from fdfgen import forge_fdf
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.getcwd())
filename_prefix = "NVC"
xml_file = "Adeldian.xml"
pdf_file = "Blank_Character_Sheet.pdf"
tmp_file = "tmp.fdf"
output_folder = './output/'

def add_xml_data(field_name, xml_find_string):
  global fields, xml

  fields.append((field_name,xml.find(xml_find_string).text))

def add_raw_data(field_name, data):
  global fields
  fields.append((field_name,data))

def character_info(xml):
  add_xml_data('CharacterName','./character/name')
  add_xml_data('CharacterName 2','./character/name')

  level = str(xml.find('./character/class/level').text)
  player_class = str(xml.find('./character/class/name').text)
  add_raw_data('ClassLevel','Level ' + level + ' ' + player_class)

  add_xml_data('Background','./character/background/name')
  add_xml_data('Race','./character/race/name')

  return level

def combat_info(xml):
    add_xml_data('HPMax','./character/hpMax')


def ability_scores_and_modifiers(xml):
  abilities = xml.find('./character/abilities').text.split(',')
  ability_modifiers = []
  race_modifiers = xml.findall('./character/race/mod')

  for mod in race_modifiers:
    if mod.find('category').text == '1':
      abilities[int(mod.find('type').text)] = int(abilities[int(mod.find('type').text)]) + int(mod.find('value').text)

  for i in range(0,6):
    ability_modifiers.append((int(abilities[i]) - 10) // 2)

  add_raw_data('STRmod', '+' + str(ability_modifiers[0]))
  add_raw_data('STR', abilities[0])
  add_raw_data('DEXmod ', '+' + str(ability_modifiers[1]))
  add_raw_data('DEX', abilities[1])
  add_raw_data('CONmod', '+' + str(ability_modifiers[2]))
  add_raw_data('CON', abilities[2])
  add_raw_data('INTmod', '+' + str(ability_modifiers[3]))
  add_raw_data('INT', abilities[3])
  add_raw_data('WISmod', '+' + str(ability_modifiers[4]))
  add_raw_data('WIS', abilities[4])
  add_raw_data('CHamod', '+' + str(ability_modifiers[5]))
  add_raw_data('CHA', abilities[5])
  
  return ability_modifiers

def proficiency(level):
  proficiency_modifier = (int(level) - 1 )// 4 + 2
  add_raw_data('ProfBonus','+' + str(proficiency_modifier))
  return proficiency_modifier

def skill_modifiers(ability_modifiers,proficiency_modifier):

  # Skill Proficiencies
  skills = ('Acrobatics', 'Animal', 'Arcana', 'Athletics', 'Deception ',\
   'History ','Insight','Intimidation','Investigation ','Medicine','Nature',\
   'Perception ', 'Performance','Persuasion','Religion','SleightofHand','Stealth ','Survival')
  abilities_for_skills = (1,4,3,0,5,3,4,5,3,4,3,4,5,5,3,1,1,4)
  race_proficiencies = xml.findall('./character/race/proficiency')
  class_proficiencies = xml.findall('./character/class/feat/proficiency')
  background_proficiencies = xml.findall('./character/background/proficiency')
  filled = []
  for i in range(0,len(skills)):
    for proficiency in race_proficiencies:
      if int(proficiency.text) - 100 == i:
        add_raw_data(skills[i], '+' + str(int(ability_modifiers[abilities_for_skills[i]]) + int(proficiency_modifier)))
        add_raw_data('Check Box ' + str(i+23),'Yes')
        filled.append(i)
    for proficiency in class_proficiencies:
      if int(proficiency.text) - 100 == i:
        add_raw_data(skills[i], '+' + str(int(ability_modifiers[abilities_for_skills[i]]) + int(proficiency_modifier)))
        add_raw_data('Check Box ' + str(i+23),'Yes')
        filled.append(i)
    for proficiency in background_proficiencies:
      if int(proficiency.text) - 100 == i:
        add_raw_data(skills[i], '+' + str(int(ability_modifiers[abilities_for_skills[i]]) + int(proficiency_modifier)))
        add_raw_data('Check Box ' + str(i+23),'Yes')
        filled.append(i)

  # skills without proficiency
  for i in range(0,len(skills)):
    if not i in filled:
        add_raw_data(skills[i], '+' + str(int(ability_modifiers[abilities_for_skills[i]])))

  # passive perception
  
def saving_throws(ability_modifiers,proficiency_modifier):
  #saving throws
  st_proficiencies = xml.findall('./character/class/proficiency')
  st_fields = ('ST Strength', 'ST Dexterity', 'ST Constitution', 'ST Intelligence','ST Wisdom','ST Charisma')
  st_filled = []
  for i in range(0,len(st_fields)):
    for proficiency in st_proficiencies:
      if int(proficiency.text) == i:
        add_raw_data(st_fields[i], '+' + str(int(ability_modifiers[i]) + int(proficiency_modifier)))
        if i == 0:
          add_raw_data('Check Box 11','Yes')
        else:
          add_raw_data('Check Box ' + str(i+17),'Yes')
        st_filled.append(i)

  for i in range(0,len(st_fields)):
    if not i in st_filled:
      add_raw_data(st_fields[i], '+' + str(int(ability_modifiers[i])))


def process_xml(file):
  global fields, xml
  fields = []

  with open(file, 'r') as xml_file:
    data=xml_file.read().replace('\n', '')
    xml=ET.fromstring(data)

  level = character_info(xml)
  combat_info(xml)
  ability_modifiers = ability_scores_and_modifiers(xml)
  proficiency_modifier = proficiency(level)
  skill_modifiers(ability_modifiers,proficiency_modifier)
  saving_throws(ability_modifiers,proficiency_modifier)

def form_fill(fields):

  fdf = forge_fdf("",fields,[],[],[])
  fdf_file = open(tmp_file,"wb")
  fdf_file.write(fdf)
  fdf_file.close()
  output_file = '{0}{1}.pdf'.format(output_folder, 'Adeldian')
  cmd = 'pdftk "{0}" fill_form "{1}" output "{2}" dont_ask'.format(pdf_file, tmp_file, output_file)
  #print(cmd)
  os.system(cmd)
  os.remove(tmp_file)

process_xml(xml_file)
form_fill(fields)