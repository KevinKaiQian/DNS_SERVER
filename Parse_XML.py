#!/usr/bin/env python
#_*_ coding:utf-8 _*_
import xml.dom.minidom 
#minidom���ڽ���xml�ļ�

#����__entity__��__Parameter__����
__entity__={}
__Parameter__={}

class Collect_entity(object):
  
	#selfָ����ʵ��������ʵ�ʾ���oject
    def __init__(self):
        #pass�ǿ���䲻���κ�����,ֻ��Ϊ�˱��ֳ����������
        pass

    def entity(self):
        #read all XML content to memory
        TestTree = xml.dom.minidom.parse("Config.xml") 
		#XML convert tree and get Element 
        self.elemt = TestTree.documentElement 

		#Get tree node element entity
        entitys = self.elemt.getElementsByTagName("entity") 
  
        for item in entitys:

            try:
                
                IP_address = item.getElementsByTagName('IP_address')[0] 
                Name = item.getElementsByTagName('Name')[0]
				#childnodes��ȡ����<Name>www.ccc.com</Name>��childNodes[0]��ʾһ���ڵ�
                __entity__[Name.childNodes[0].data]=IP_address.childNodes[0].data
               
                
            except Exception:
                pass
 
        return __entity__

    def Parameter(self):

        if self.elemt.hasAttribute("Address"): 
            __Parameter__['Address']=self.elemt.getAttribute('Address')
        if self.elemt.hasAttribute("port"): 
            __Parameter__['port']=self.elemt.getAttribute('port')
        if self.elemt.hasAttribute("mode"): 
            __Parameter__['mode']=self.elemt.getAttribute('mode')
        
        return __Parameter__

if __name__=='__main__':
    kk = Collect_entity()
    value = kk.entity()



