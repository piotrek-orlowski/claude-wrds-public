/* Metadata only: one daily member, no observation reads. */
options notes source errorabend;
%let output_dir=%sysget(HOME)/scratch/wrds_taq_inventory;

proc contents data=taqmsec.ctm_20241007
  out=work.probe_columns(keep=libname memname name type length varnum label format informat)
  noprint;
run;

proc sort data=work.probe_columns;
  by varnum;
run;

proc export data=work.probe_columns
  outfile="&output_dir./taq_metadata_probe_20261005T222724_columns.csv"
  dbms=csv replace;
run;

proc sql;
  create table work.taq_libraries as
  select libname, engine, path
  from dictionary.libnames
  where substr(upcase(libname),1,3)='TAQ'
  order by libname,path;
quit;

proc export data=work.taq_libraries
  outfile="&output_dir./taq_metadata_probe_20261005T222724_libraries.csv"
  dbms=csv replace;
run;

%put TAQ_METADATA_PROBE_COMPLETE SYSCC=&syscc.;
