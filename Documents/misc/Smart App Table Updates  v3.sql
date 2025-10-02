/*
CHANNELS WHERE THE CLAIMS ARE ARRIVING
***************************************
*/
create table Claim_channels
(
Id number not null constraint pk_claim_channels primary key, 
Channel_name varchar2(100),
Channel_desc varchar2(500),
status varchar2(10)
);
--------Sequence--------------------------------
create sequence sqClaimchannelsID start with 1 increment by 1 nocache;

insert into Claim_channels (Id,Channel_name,Channel_desc,status) values (sqClaimchannelsID.Nextval,'SMART APPLICATIONS','HEALTH INSURANCE','TRUE');
commit;
--insert into Claim_channels (Id,Channel_name,Channel_desc,status) values (sqClaimchannelsID.Nextval,'NEXT MICRO SOLUTIONS','HEALTH INSURANCE','TRUE');
--commit; 
--select * from Claim_channels for update;
--select * from stg_claims;
/*
***************************************
STAGING TABLE FOR CLAIMS ARRIVING
***************************************
*/
create table stg_claims
(
Id number not null constraint pk_stg_claims primary key,
cId varchar2(50) not null, 
cindex number,
channelid number,
schemeCode varchar2(20) not null, 
providerCode varchar2(20) not null, 
memberNumber varchar2(20) not null, 
benefitId number, 
memberNames varchar2(150) not null,
invoiceDate date, 
amount number(18,4), 
dateReceived varchar2(20), 
invoiceNumber varchar2(20),
status varchar2(10),
clnBenClauseCode varchar2(50), 
cardSerialNumber varchar2(20), 
insertDate varchar2(20),
providerClaimId varchar2(50),
quantity varchar2(10), 
ipAddress varchar2(20),
poolNr varchar2(20), 
claimNr varchar2(20),
receiptNr varchar2(20),
patientFileNr varchar2(20),
csource varchar2(20), 
admitId varchar2(20), 
attendantId varchar2(20),
invoiceBatchNr varchar2(20),
patientMedicalAidCode varchar2(20),
patientMedicalAidPlan varchar2(20), 
policyId varchar2(20),
policyCurrencyCode varchar2(20),
policyConvRate varchar2(20),
localCurrencyCode varchar2(20),
localConvRate varchar2(20),
serviceType varchar2(20),
diagnosisCode varchar2(20),
diagnosisDescription varchar2(20),
staffNumber varchar2(20), 
countryCode varchar2(10),
roamingAmount number(18,4), 
roamingCountry varchar2(20),
processed number(10),
loadedDate date default sysdate
);
create sequence sqstgclaimsId start with 1 increment by 1 nocache;
/*
*****************************************************
Claim service details
select * from stg_claims;
select * from stg_claimsServices;

delete from stg_claims;
delete from stg_claimsServices;
update stg_claims set processed=2;
commit;
*****************************************************
*/
create table stg_claimsServices
(
Id number not null constraint pk_stg_claims_services primary key,
claimId varchar2(50),
serviceType varchar2(50),
serviceCodeType varchar2(50),
serviceCode varchar2(50),
serviceDescription varchar2(100),
quantity number(10),
amount number(18,4),
diagnosisCodeType varchar2(50),
diagnosisCode varchar2(50),
diagnosisDescription varchar2(100),
receivedDate date, 
admitId varchar2(10), 
pickedStatus varchar2(10), 
pickedDate varchar2(15), 
providerKey varchar2(20), 
invoiceNr varchar2(15), 
insurerId varchar2(15),
status varchar2(10)
);
create sequence sqstgclaimsserviceId start with 1 increment by 1 nocache;
/*
Upload Temp Tables
******************************************************************************
*/
create table claims_first_id
(
       first_id number(10)
);
create table claims_last_id
(
       claims_last_id number(10)
);
create table detail_first_id
(
       first_id number(10)
);
create table detail_last_id
(
       id number(10)
);
/*
Production table updates
*************************************************************************
*/
/*
Used to indicate uploads to Third parties that track records
************************************************************************
*/
create table service_item_uploads
(
id number(10),
item_id number(10),
item_code varchar(50),
item_type number(10),/* 1=Members, 2=Schemes, 3=benefits*/
channel_id number(10),
state number(10), /* 0=Not Sent, 1=Sent, 3=Recieved*/
created_date date,
status varchar(5)
);
create sequence sqserviceitemuploadsId start with 1 increment by 1 nocache;
/*
Used to Track the Types of the Item Types
************************************************************************
*/
create table service_item_types
(
id number(10),
service_type_name varchar2(50),
service_type_descr varchar2(250),
status varchar(5)
);
create sequence sqservice_item_typesId start with 1 increment by 1 nocache;
---------Load temp data------------------------------------------------------
begin
insert into service_item_types values (sqservice_item_typesId.Nextval,'MEMBERS','MEMBER DETAILS','TRUE');
insert into service_item_types values (sqservice_item_typesId.Nextval,'SCHEMES','SCHEME DETAILS','TRUE');
insert into service_item_types values (sqservice_item_typesId.Nextval,'BENEFITS','BENEFIT DETAILS','TRUE');
commit;
end;
/*
Used to Track the Types of the Item Types
************************************************************************
*/


