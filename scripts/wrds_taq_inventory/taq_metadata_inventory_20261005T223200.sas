/* Metadata only. Never select observations from TAQ members. */
options notes source errorabend;
%let output_dir=%sysget(HOME)/scratch/wrds_taq_inventory;
%let run=taq_metadata_inventory_20261005T223200;

proc sql;
  create table work.taq_libraries as
  select distinct libname,engine,path
  from dictionary.libnames
  where libname in ('TAQ','TAQMSEC','TAQSAMP','TAQMSAMP')
  order by libname,path;

  create table work.taq_members as
  select distinct libname,memname,memtype,memlabel,nvar,nobs,
         crdate format=datetime26.6,modate format=datetime26.6
  from dictionary.tables
  where libname in ('TAQ','TAQMSEC','TAQSAMP','TAQMSAMP')
    and memtype='DATA'
  order by libname,memname;

  create table work.taq_columns as
  select distinct libname,memname,name,type,length,varnum,label,format,informat
  from dictionary.columns
  where libname in ('TAQ','TAQMSEC','TAQSAMP','TAQMSAMP')
    and memtype='DATA'
  order by libname,memname,varnum;
quit;

/* Fixed-length hashes of every field avoid ambiguous delimiter concatenation.
   Ordered MD5 chains identify equal metadata layouts, not observation content. */
data work.taq_layout_map;
  set work.taq_columns;
  by libname memname varnum;
  length layout_id $32;
  retain layout_id column_count;
  if first.memname then do;
    layout_id='';
    column_count=0;
  end;
  column_count+1;
  layout_id=put(md5(cats(
    layout_id,
    put(md5(strip(put(varnum,best32.))),hex32.),
    put(md5(trim(name)),hex32.),
    put(md5(trim(type)),hex32.),
    put(md5(strip(put(length,best32.))),hex32.),
    put(md5(trim(label)),hex32.),
    put(md5(trim(format)),hex32.),
    put(md5(trim(informat)),hex32.)
  )),hex32.);
  if last.memname then output;
  keep libname memname layout_id column_count;
run;

proc sort data=work.taq_layout_map out=work.sorted_layout_map;
  by layout_id libname memname;
run;

data work.layout_representatives;
  set work.sorted_layout_map;
  by layout_id;
  if first.layout_id;
run;

proc sql;
  create table work.taq_layout_columns as
  select r.layout_id,c.*
  from work.taq_columns as c
  inner join work.layout_representatives as r
    on c.libname=r.libname and c.memname=r.memname
  order by r.layout_id,c.varnum;

  create table work.taq_validation as
  select t.libname,t.memname,t.nvar,m.column_count,m.layout_id,
         (t.nvar=m.column_count) as column_count_matches
  from work.taq_members as t
  left join work.taq_layout_map as m
    on t.libname=m.libname and t.memname=m.memname
  where missing(m.layout_id) or t.nvar ne m.column_count;
quit;

%macro export_metadata(table,suffix);
  proc export data=work.&table.
    outfile="&output_dir./&run._&suffix..csv"
    dbms=csv replace;
  run;
%mend;
%export_metadata(taq_libraries,libraries);
%export_metadata(taq_members,members);
%export_metadata(taq_layout_map,layout_map);
%export_metadata(taq_layout_columns,layout_columns);
%export_metadata(taq_validation,validation);

%put TAQ_METADATA_INVENTORY_COMPLETE SYSCC=&syscc.;
