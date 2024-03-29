from __future__ import division
from __future__ import print_function

import logging
from Doom.module import logger
from Doom.module.smbclient import MiniImpacketShell
from impacket.smbconnection import SMBConnection
from impacket import LOG
from Doom.module.color import C

class SMB_ENUM(object):

    def __init__(self,ip="",user="Guest",password=""):
        self.target = ip
        self.port = 445
        self.user = user
        self.password = password
        self.ignore_share = ["IPC$"]
        self.avaliable_opt = ["target","user","password"]
        logger.init()

    def set_target(self, ip):
        self.target = ip
        print("TARGET => %s" % self.target)


    def set_user(self, user):
        self.user = user
        print("USER => %s" % self.user)

    def set_password(self, password):
        self.password = password
        print("PASSWORD => %s" % self.password)

    def show_help(self):
        print("\n\tShow available commands for current module\n")
        print("\thelp - print this help")
        print("\tshow options - list available options")
        print("\tset - use to set required options\n")

    def show_options(self):
        print("\n\tShow Available options for current module\n")
        print("\tTARGET - REMOTE TARGET IP ADDRESS")
        print("\tUSER - USER NAME USE TO AUTHENTICATE TO REMOTE SERVER (OPTIONAL)")
        print("\tPASSWORD - PASSWORD  USE TO AUTHENTICATE TO REMOTE SERVER (OPTIONAL)\n")

        print("\n\tCurrent Settings\n")

        if self.target != "":
            print("\tTARGET - %s" % self.target)
        if self.user != "Guest":
            print("\tUSER - %s" % self.user)
        if self.password != "":
            print("\tPASSWORD - %s" % self.password)

    def tryLogin(self):
        '''
            Setup a connection with smb server, authenticate using the give user name and password. if the user name and
            password is not specify use guest as login. If successfully authenticated create an interactive section between
            smb server and client
        :return:
        '''

        try:

            # Setup SMB Connection and Create an interactive shell

            logging.info("Trying To Authenticate As %s ..." % self.user)
            self.smbClient = SMBConnection(self.target,self.target,sess_port=self.port)
            self.smbClient.login(self.user,self.password)
            logging.info("Successfully Login As %s ..." % self.user)
            self.shell = MiniImpacketShell(self.smbClient)


        except Exception as e:
            LOG.level = logging.DEBUG
            if logging.getLogger().level == logging.DEBUG:
                import traceback
                traceback.print_exc()
            logging.error(str(e))

    def recursive_dirlist(self,directory_list,share=""):
        '''
            List for file and directory recursively according to their permission.
        :param directory_list:
        :param share:
        :return:
        '''

        if len(directory_list) != 0:
            for directory in directory_list:
                LOG.info("Listing File And Directory For Path \\\\%s\\%s" % (share, directory))
                print("\n")
                self.shell.do_cd(directory)
                directory_list = self.shell.do_ls('')
                print("\n")
                temp_share = share
                if len(directory_list) != 0 :
                    share += "\\" +directory
                    self.recursive_dirlist(directory_list,share)
                else:
                    self.shell.do_cd("..")
                    share = temp_share


    def enumerateShares(self):
        '''

        :return:
        '''

        shares = self.shell.do_shares("shares")
        shares_list = []
        logging.info("Listing Shares")
        logging.getLogger().level = logging.DEBUG
        for i in range(len(shares)):
            share = shares[i]['shi1_netname'][:-1]
            logging.debug(share)
            if share not in self.ignore_share:
                if self.smbClient.isGuestSession() > 0:
                    if "$" not in share:
                        shares_list.append(share)
                else:
                    shares_list.append(share)

        LOG.level = logging.INFO
        print("\n")

        if len(shares_list) != 0:
            for share in shares_list:
                try:
                    LOG.info("Listing File And Directory For Share %s \n" % share)
                    self.shell.do_use(share)
                    directory_list = self.shell.do_ls('')
                    print("\n")
                    if "$" not in share:
                        self.recursive_dirlist(directory_list,share)

                except Exception as e:
                    LOG.level = logging.DEBUG
                    if logging.getLogger().level == logging.DEBUG:
                        import traceback
                        #traceback.print_exc()
                    logging.error(str(e))
                    print("\n")

    def run(self):
        try:
            self.tryLogin()
            self.enumerateShares()
        except:
            pass
