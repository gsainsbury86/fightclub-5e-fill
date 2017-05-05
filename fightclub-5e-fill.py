#!/usr/local/bin/python3
import csv
from fdfgen import forge_fdf
import os
import sys
import xml.etree.ElementTree as ET
import re

sys.path.insert(0, os.getcwd())
filename_prefix = "NVC"
name = "Lophelios Cnidariath"
xml_file = name + ".xml"
pdf_file = "Blank_Character_Sheet.pdf"
tmp_file = "tmp.fdf"
output_folder = './output/'

def add_xml_data(field_name, xml_find_string):
  global fields, xml
  fields[field_name] = xml.find(xml_find_string).text

def add_custom_data(field_name, data):
  global fields
  fields[field_name] = data

def append_custom_data(field_name, data, delimiter):
  global fields
  fields[field_name]+=delimiter+data

def character_info(xml):
  global level, player_class
  # TODO: multiclass support
  level = str(xml.find('./character/class/level').text)
  player_class = str(xml.find('./character/class/name').text)
  
  add_custom_data('ClassLevel','Level ' + level + ' ' + player_class)


def background_info(xml):

  feats = xml.findall('./character/background/feat')

  for feat in feats:
    if feat.find('name').text == 'Personality Trait':
      add_custom_data('PersonalityTraits ',feat.find('text').text)
    if feat.find('name').text == 'Ideal':
      add_custom_data('Ideals',feat.find('text').text)
    if feat.find('name').text == 'Bond':
      add_custom_data('Bonds',feat.find('text').text)
    if feat.find('name').text == 'Flaw':
      add_custom_data('Flaws',feat.find('text').text)

  feats_text = ""

  for feat in feats:
    feats_text+= feat.find('name').text+"\r\n"
    feats_text+= feat.find('text').text+"\r\n"

  add_custom_data('Feat+Traits',feats_text)


def combat_info(xml,ability_modifiers):
  add_custom_data('Initiative', ('+' if int(ability_modifiers[1]) >= 0 else '') + str(ability_modifiers[1]))
  #TODO: add default speed
  add_custom_data('Speed', '30 ft')

def ability_scores_and_modifiers(xml):
  abilities = xml.find('./character/abilities').text.split(',')
  ability_modifiers = []
  race_modifiers = xml.findall('./character/race/mod')

  for mod in race_modifiers:
    if mod.find('category').text == '1':
      abilities[int(mod.find('type').text)] = int(abilities[int(mod.find('type').text)]) + int(mod.find('value').text)

  for i in range(0,6):
    ability_modifiers.append((int(abilities[i]) - 10) // 2)

  add_custom_data('STRmod', ('+' if ability_modifiers[0] >= 0 else '') + str(ability_modifiers[0]))
  add_custom_data('STR', abilities[0])
  add_custom_data('DEXmod ',('+' if ability_modifiers[1] >= 0 else '') + str(ability_modifiers[1]))
  add_custom_data('DEX', abilities[1])
  add_custom_data('CONmod', ('+' if ability_modifiers[2] >= 0 else '') + str(ability_modifiers[2]))
  add_custom_data('CON', abilities[2])
  add_custom_data('INTmod', ('+' if ability_modifiers[3] >= 0 else '') + str(ability_modifiers[3]))
  add_custom_data('INT', abilities[3])
  add_custom_data('WISmod', ('+' if ability_modifiers[4] >= 0 else '') + str(ability_modifiers[4]))
  add_custom_data('WIS', abilities[4])
  add_custom_data('CHamod', ('+' if ability_modifiers[5] >= 0 else '') + str(ability_modifiers[5]))
  add_custom_data('CHA', abilities[5])
  
  return ability_modifiers

def proficiency(level):
  proficiency_modifier = (int(level) - 1 )// 4 + 2
  add_custom_data('ProfBonus','+' + str(proficiency_modifier))
  return proficiency_modifier

def skill_modifiers(ability_modifiers,proficiency_modifier):

  # Skill Proficiencies
  skills = ('Acrobatics', 'Animal', 'Arcana', 'Athletics', 'Deception ',\
   'History ','Insight','Intimidation','Investigation ','Medicine','Nature',\
   'Perception ', 'Performance','Persuasion','Religion','SleightofHand','Stealth ','Survival')
  abilities_for_skills = (1,4,3,0,5,3,4,5,3,4,3,4,5,5,3,1,1,4)
  race_proficiencies = xml.findall('./character/race/proficiency')
  class_proficiencies = xml.findall('./character/class/proficiency')
  background_proficiencies = xml.findall('./character/background/proficiency')
  skill_modifiers = list(abilities_for_skills)
  filled = []
  for i in range(0,len(skills)):
    for proficiency in race_proficiencies:
      if int(proficiency.text) - 100 == i:
        skill_modifiers[i] = str(int(ability_modifiers[abilities_for_skills[i]]) + int(proficiency_modifier))
        add_custom_data(skills[i], ('+' if int(skill_modifiers[i]) >= 0 else '') + skill_modifiers[i])
        add_custom_data('Check Box ' + str(i+23),'Yes')
        filled.append(i)
    for proficiency in class_proficiencies:
      if int(proficiency.text) - 100 == i:
        skill_modifiers[i] = str(int(ability_modifiers[abilities_for_skills[i]]) + int(proficiency_modifier))
        add_custom_data(skills[i], ('+' if int(skill_modifiers[i]) >= 0 else '') + skill_modifiers[i])        
        add_custom_data('Check Box ' + str(i+23),'Yes')
        filled.append(i)
    for proficiency in background_proficiencies:
      if int(proficiency.text) - 100 == i:
        skill_modifiers[i] = str(int(ability_modifiers[abilities_for_skills[i]]) + int(proficiency_modifier))
        add_custom_data(skills[i], ('+' if int(skill_modifiers[i]) >= 0 else '') + skill_modifiers[i])        
        add_custom_data('Check Box ' + str(i+23),'Yes')
        filled.append(i)

  # skills without proficiency
  for i in range(0,len(skills)):
    if not i in filled:
        skill_modifiers[i] = str(int(ability_modifiers[abilities_for_skills[i]]))
        add_custom_data(skills[i], ('+' if int(skill_modifiers[i]) >= 0 else '') + skill_modifiers[i])

  # passive perception
  add_custom_data('Passive',10 + int(skill_modifiers[11]))

def saving_throws(ability_modifiers,proficiency_modifier):
  #saving throws
  st_proficiencies = xml.findall('./character/class/proficiency')
  st_fields = ('ST Strength', 'ST Dexterity', 'ST Constitution', 'ST Intelligence','ST Wisdom','ST Charisma')
  st_filled = []
  for i in range(0,len(st_fields)):
    for proficiency in st_proficiencies:
      if int(proficiency.text) == i:
        add_custom_data(st_fields[i], '+' + str(int(ability_modifiers[i]) + int(proficiency_modifier)))
        if i == 0:
          add_custom_data('Check Box 11','Yes')
        else:
          add_custom_data('Check Box ' + str(i+17),'Yes')
        st_filled.append(i)

  for i in range(0,len(st_fields)):
    if not i in st_filled:
      add_custom_data(st_fields[i], ('+' if ability_modifiers[i] >=0 else '') + str(ability_modifiers[i]))

def features_and_traits(xml):
  # Feat+Traits - page 2
  feat_text = ''
  feats = xml.findall('./character/class/feat') + xml.findall('./character/race/feat')
  for feat in feats:
    if 'Speed' in feat.find('name').text:
      append_custom_data('Speed',re.findall(r"[0-9]+",feat.find('text').text)[0] +'(' + re.findall(r'([a-zA-Z]*)ing',feat.find('text').text)[0]+ ')','/\r\n')
    else:
      feat_text+= feat.find('name').text + ':\r\n' + feat.find('text').text.replace('•','\r\n•')+"\r\n"
  add_custom_data('Features and Traits',feat_text)

def simple_fields(xml):
  with open('simple-field-mapping.csv', newline='') as csvfile:
    spamreader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
      add_xml_data(row['field'], row['path'])

def process_xml(file):
  global fields, xml, level
  fields = {}

  with open(file, 'r') as xml_file:
    data=xml_file.read().replace('\n', '')
    xml=ET.fromstring(data)

  # must be first because level is calculated
  character_info(xml)


  proficiency_modifier = proficiency(level)

  simple_fields(xml)
  background_info(xml)
  ability_modifiers = ability_scores_and_modifiers(xml)
  combat_info(xml,ability_modifiers)
  skill_modifiers(ability_modifiers,proficiency_modifier)
  saving_throws(ability_modifiers,proficiency_modifier)
  # TODO: Add all feats, not just first. Can work out how many per page based on length.
  # TODO: Calculate bonuses given from feats.
  features_and_traits(xml)


def form_fill(fields):

  fdf = forge_fdf("",fields,[],[],[])
  fdf_file = open(tmp_file,"wb")
  fdf_file.write(fdf)
  fdf_file.close()
  output_file = '{0}{1}.pdf'.format(output_folder, name)
  cmd = 'pdftk "{0}" fill_form "{1}" output "{2}" dont_ask'.format(pdf_file, tmp_file, output_file)
  #print(cmd)
  os.system(cmd)
  os.remove(tmp_file)

process_xml(xml_file)
form_fill(fields)