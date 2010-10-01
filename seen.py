#$ neutron_plugin 01
# --*-- encoding: utf-8 --*--
import re

def handler_seen(type,source,parameters):
    groupchat = get_groupchat(source)
    if parameters:
        if re.match('wasd22', parameters):
            msg(groupchat, u'A po4emu vi sprashivaete?')
        elif re.match('maxally', parameters):
            msg(groupchat, u'!maxally')
        elif GROUPCHATS[groupchat].has_key(parameters):
            msg(groupchat, u'Ya ego vizhu! O_O')
        else:
            msg(groupchat, u'Netu ego.')
    else:
        msg(groupchat, u'Kakie vashi dokazatelstva?!')
        
        
def handler_bor2(type,source,parameters):
    groupchat = get_groupchat(source)
    msg(groupchat, u'[:||||:]')
    
def handler_leave_seen(groupchat, nick):
    msg(groupchat, u'Ushol '+nick);
    

register_command_handler(handler_seen,u'!seen',0,u'seen',u'!seen',[u'!seen'])
register_command_handler(handler_bor2,u'!bor',0,u'bor',u'!bor',[u'!bor'])
register_leave_handler(handler_leave_seen)
