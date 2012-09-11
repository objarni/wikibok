#!/usr/bin/python
# -- coding: utf-8 --
#
# Copyright 2009 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


__author__ = 'e.bidelman (Eric Bidelman)'

import getopt
import mimetypes
import os.path
import sys

import gdata.sample_util
import gdata.sites.client
import gdata.sites.data


SOURCE_APP_NAME = 'wikibok'

MAIN_MENU = [u'1) Lista böcker',
             u'2) Lista senaste ändringar',
             u'3) Skapa ny bok',
             u'4) Ta bort bok',
             u'5) Avsluta']

SETTINGS_MENU = ['1) Change current site.',
                 '2) Change domain.']


class SitesExample(object):
  """Wrapper around the Sites API functionality."""

  def __init__(self, site_name=None, site_domain=None, debug=False):
    #if site_domain is None:
    #  site_domain = self.PromptDomain()

    if site_name is None:
      site_name = 'motargumentwiki' #self.PromptSiteName()

    mimetypes.init()

    self.client = gdata.sites.client.SitesClient(
        source=SOURCE_APP_NAME, site=site_name, domain=site_domain)
    self.client.http_client.debug = debug

    try:
      gdata.sample_util.authorize_client(
          self.client, service=self.client.auth_service, source=SOURCE_APP_NAME,
          scopes=['http://sites.google.com/feeds/',
                  'https://sites.google.com/feeds/'],
          auth_type = gdata.sample_util.CLIENT_LOGIN)
    except gdata.client.BadAuthentication:
      exit('Invalid user credentials given.')
    except gdata.client.Error:
      exit('Login Error')

  def PrintMainMenu(self):
    """Displays a menu of options for the user to choose from."""
    print '\n~~~ wikibok.py huvudmenu ~~~'
    print '=============================='
    print '\n'.join(MAIN_MENU)
    print '==============================\n'

  def PrintSettingsMenu(self):
    """Displays a menu of settings for the user change."""
    print '\nSites API Sample > Settings'
    print '================================'
    print '\n'.join(SETTINGS_MENU)
    print '================================\n'

  def GetMenuChoice(self, menu):
    """Retrieves the menu selection from the user.

    Args:
      menu: list The menu to get a selection from.

    Returns:
      The integer of the menu item chosen by the user.
    """
    max_choice = len(menu)
    while True:
      user_input = raw_input('^^ ')

      try:
        num = int(user_input)
      except ValueError:
        continue

      if num <= max_choice and num > 0:
        return num

  def PromptSiteName(self):
    site_name = ''
    while not site_name:
      site_name = raw_input('site name: ')
      if not site_name:
        print 'Please enter the name of your Google Site.'
    return site_name

  def PromptDomain(self):
    return raw_input(('If your Site is hosted on a Google Apps domain, '
                      'enter it (e.g. example.com): ')) or 'site'

  def GetChoiceSelection(self, feed, message):
    for i, entry in enumerate(feed.entry):
      print '%d.) %s' % (i + 1, entry.title.text)
    choice = 0
    while not choice or not 0 <= choice <= len(feed.entry):
      choice = int(raw_input(message))
    print
    return choice

  def PrintEntry(self, entry):
    print '%s [%s]' % (entry.title.text, entry.Kind())
    if entry.page_name:
      print ' page name:\t%s' % entry.page_name.text
    if entry.content:
      print ' content\t%s...' % str(entry.content.html)[0:100]

  def PrintListItem(self, entry):
    print '%s [%s]' % (entry.title.text, entry.Kind())
    for col in entry.field:
      print ' %s %s\t%s' % (col.index, col.name, col.text)

  def PrintListPage(self, entry):
    print '%s [%s]' % (entry.title.text, entry.Kind())
    for col in entry.data.column:
      print ' %s %s' % (col.index, col.name)

  def PrintFileCabinetPage(self, entry):
    print '%s [%s]' % (entry.title.text, entry.Kind())
    print ' page name:\t%s' % entry.page_name.text
    print ' content\t%s...' % str(entry.content.html)[0:100]

  def PrintAttachment(self, entry):
    print '%s [%s]' % (entry.title.text, entry.Kind())
    if entry.summary is not None:
      print ' description:\t%s' % entry.summary.text
    print ' content\t%s, %s' % (entry.content.type, entry.content.src)

  def PrintWebAttachment(self, entry):
    print '%s [%s]' % (entry.title.text, entry.Kind())
    if entry.summary.text is not None:
      print ' description:\t%s' % entry.summary.text
    print ' content src\t%s' % entry.content.src

  def Run(self):
    """Executes the demo application."""

    try:
      while True:
        self.PrintMainMenu()
        choice = self.GetMenuChoice(MAIN_MENU)

        if choice == 1:
          print 'kommer i framtiden'

        if choice == 2:
          print u"\nKollar vad som hänt på det senaste...\n"

          feed = self.client.GetActivityFeed()
          for entry in feed.entry[0:10]:
            print '  %s [%s on %s]' % (entry.title.text, entry.Kind(),
                                       entry.updated.text)

        if choice == 3:
          print "\nFetching content feed of '%s'...\n" % self.client.site

          feed = self.client.GetContentFeed()
          try:
            selection = self.GetChoiceSelection(
                feed, 'Select a parent to upload to (or hit ENTER for none): ')
          except ValueError:
            selection = None

          page_title = raw_input('Enter a page title: ')

          parent = None
          if selection is not None:
            parent = feed.entry[selection - 1]

          new_entry = self.client.CreatePage(
              'webpage', page_title, 'lite html',
              parent=parent)
          if new_entry.GetAlternateLink():
            print 'Created. View it at: %s' % new_entry.GetAlternateLink().href

        if choice == 4:
          print 'ta bort bok ej implementerat\n'

        if choice == 5:
          print 'Ha det!\n'
          return

    except gdata.client.RequestError, error:
      print error
    except KeyboardInterrupt:
      return


def main():
  """The main function runs the SitesExample application."""

  print u'~~~ Välkommen till wikibok.py! ^^ ~~~\n'

  try:
    opts, args = getopt.getopt(sys.argv[1:], '',
                               ['site=', 'domain=', 'debug'])
  except getopt.error, msg:
    print """python sites_sample.py --site [sitename]
                                    --domain [domain or "site"]
                                    --debug [prints debug info if set]"""
    sys.exit(2)

  site = None
  domain = None
  debug = False

  for option, arg in opts:
    if option == '--site':
      site = arg
    elif option == '--domain':
      domain = arg
    elif option == '--debug':
      debug = True

  sample = SitesExample(site, domain, debug=debug)
  sample.Run()


if __name__ == '__main__':
  main()
