# Deployment Notes

Here are the steps that Mike Simpson went through to deploy the
production instance of the patron groups software in October 2019.

## Prerequisites

*   An IAM account with administrative access in the Library's main
    AWS account.
    
*   An existing VPC in that account.

*   An existing public subnet on that VPC.

## Deployment

### Creation of RancherOS-based EC2 instance.

In the AWS Console, logged in via the "mgsimpson" IAM account, pointed
at the "Oregon (US-West-2)" AWS region:

*   (DONE PREVIOUSLY, NO NEED TO REPEAT) In the "Security Group"
    section of the EC2 module, created the "PatronETL" security group
    to limit access to the host that would be created in the following
    step.
    
*   (DONE PREVIOUSLY, NO NEED TO REPEAT) In the "Key Pairs" section of
    the EC2 module, created the "PatronETL" key pair and downloaded
    and saved a local copy.

*   In the "Instances" section of the EC2 module, selected "Launch
    Instance", and used the following parameters:
    
        AMI Details: RancherOS - HVM
        Instance Type: t2.small
        Security Groups: PatronETL
        Network: (default VPC)
        Subnet: (first subnet on default VPC)
        Storage: (left at default 8 GB general purpose)
        
    and selected "Launch", choosing to use the existing "PatronETL"
    key pair when prompted.
    
*   In the EC2 module dashboard, changed the name of the newly-created
    EC2 instance to "Patron ETL", and waited for it to finish
    initializing.
    
*   Tested connecting to the new instance via SSH, e.g.:

        % ssh -i [path to saved key pair file] rancher@[hostname from EC2 dashboard]
        
            $ sudo ros os version
            v1.1.0
            
            $ exit

### Preparation of RancherOS instance for use.

In a terminal window on my local workstation:

*   Logged into the "Patron ETL" instance and performed upgrade:

        % ssh -i [path to saved key pair file] rancher@[hostname from EC2 dashboard]
        
            $ sudo ros os upgrade
    
                [followed prompts to upgrade to latest version]
                [upgrade finishes with reboot, which terminates SSH session]
        
        % ssh -i [path to saved key pair file] rancher@[hostname from EC2 dashboard]
        
            $ sudo ros os version
            v1.5.4
            
            $ exit
            
*   Switched to the "centos" console in RancherOS and added build dependencies:

        % ssh -i [path to saved key pair file] rancher@[hostname from EC2 dashboard]
        
            $ sudo ros console enable centos
            $ sudo reboot
            
                [SSH session terminated]

        % ssh -i [path to saved key pair file] rancher@[hostname from EC2 dashboard]
        
            $ sudo ros console list
            disabled alpine
            current  centos
            disabled debian
            disabled default
            disabled fedora
            disabled ubuntu
            
            $ sudo yum install epel-release
            $ sudo yum install git python3 python3-pip
            
            $ git --version
            git version 1.8.3.1
            
            $ python3 --version
            Python 3.6.8
            
            $ pip3 --version
			pip 9.0.3 from /usr/lib/python3.6/site-packages (python 3.6)
            
            $ exit
            
*   Note that RancherOS already includes Docker services as part of
    the base installation.

### Building and starting the patron groups service.

*   Logged into the "Patron ETL" instance and built patron groups service:

        % ssh -i [path to saved key pair file] rancher@[hostname from EC2 dashboard]
        
            $ git clone https://github.com/ualibraries/patron-groups.git ual-patron-groups
            $ cd ual-patron-groups
            $ git checkout v1.5.2
            
            $ cd src/main/python
            $ sudo pip3 install --trusted-host pypi.python.org -r requirements.txt
            $ python3 setup.py sdist
            $ cd ../../..
            
            $ cd src/main/docker
            $ cp ../python/dist/petal-1.5.2.tar.gz .
            $ docker build -t pgrps:1.5.2 .
            $ cd ../../..

            $ export LDAP_PASSWD=[ldap password]
            $ export GROUPER_PASSWD=[grouper password]
            $ export SLACK_WEBHOOK=[slack webhook]
            $ docker run -e "LDAP_PASSWD=${LDAP_PASSWD}" \
                         -e "GROUPER_PASSWD=${GROUPER_PASSWD}" \
                         -e "SLACK_WEBHOOK=${SLACK_WEBHOOK}" \
                         --rm -d pgrps:1.5.2
