#!/usr/bin/env bash

# bash
# vmd dcd read wrapper
# michaladammichalowski@gmail.com
# 01.03.16 - creation
# EXAMPLE CALL: mm_analysis_vmdloader.sh -pdb ../step5_assembly.namd.pdb -psf ../step5_assembly.xplor_ext.psf --equi '*_equilibration.dcd' --prod '*_production.dcd' --stride 1

while [[ $# > 1 ]]
do
key="$1"

case $key in
    -pdb|--pdb)
    pdb="$2"
    shift
    ;;
    -psf|--psf)
    psf="$2"
    shift
    ;;
    -e|--equi)
    equi="$2"
    shift
    ;;
    -p|--prod)
    prod="$2"
    shift
    ;;
    -s|--stride)
    stride="$2"
    shift
    ;;
    *)
    echo "Not known argument"
    ;;
esac
shift
done

equis=$(find .  -maxdepth 1 -name "$equi" -print | sort)
prods=$(find .  -maxdepth 1 -name "$prod" -print | sort)
dcds="$equis $prods"

echo -e "info: loading ${pdb} ${psf}"
echo -e "info: loaded trajectory:\n${dcds}"

# molrep hack added for proper cartoon representation if trajectory loaded in background

vmd_config="\
mol new ${pdb} first 0 last -1 step 1 filebonds 1 autobonds 1 waitfor 1\n\
mol addfile ${psf} type psf first 0 last -1 step 1 filebonds 1 autobonds 1 waitfor 1\n\
mol representation NewCartoon\n\
mol selection {protein}\n\
mol color ColorID 3\n\
mol material AOChalky\n\
mol addrep 0\n\
"

for traj in $dcds; do
    vmd_config="${vmd_config}mol addfile ${traj} type dcd first 0 last -1 step ${stride} filebonds 1 autobonds 1 waitfor all \n"
done

echo -e $vmd_config > visual.vmd
vmd -e visual.vmd