#!/bin/bash

# Filters given arguments list and produces an array containing "no-options"
# (argument prefixed with -) and options.
# Input: COMP_WORDS global array must be defined
# Output:
#   __no_opts global array, __no_opts[0] is the name of the application
#   __no_opts_cur index of word currently completed, -1 if currently completed
#                    word is an option
#   __opts global array
_filter_options()
{
    local index_no_opts=0
    local index_opts=0
    local cur_index=0
    local w
    local num_of_elems

    __no_opts_cur=-1
    num_of_elems=${#COMP_WORDS[@]}
    while (( cur_index < num_of_elems ))
    do
        w=${COMP_WORDS[${cur_index}]}
        if [[ ${w} != -* ]]
        then
            __no_opts[${index_no_opts}]=${w}
            if [[ ${cur_index} == ${COMP_CWORD} ]]
            then
                __no_opts_cur=${index_no_opts}
            fi
            ((index_no_opts++))
        else
            __opts[${index_opts}]=${w}
            ((index_opts++))
        fi
        ((cur_index++))
    done
}

_setup()
{
    declare -a __no_opts
    declare -a __opts
    declare __no_opts_cur
}

_clean()
{
    unset __no_opts
    unset __opts
    unset __no_opts_cur
}

_cortex_client()
{
    local cur opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"

    #
    #  Cortex-client's options.
    #
    opts=`${COMP_WORDS[0]} --options`
    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi

    _setup
    _filter_options

    #
    #  Cortex-client's resources and services.
    #
    local resources=`${__no_opts[0]} --resources`

    local resource=${__no_opts[1]}
    local action=${__no_opts[2]}

    #  Complete resources if no action is yet given
    if [[ ${__no_opts_cur} == 1 ]]
    then
        COMPREPLY=( $(compgen -W "${resources}" ${cur}) )
        _clean
        return 0
    fi

    #  Complete action if no argument is yet given
    if [[ ${__no_opts_cur} == 2 ]]
    then
        local actions
        actions=`${__no_opts[0]} ${resource} __available_actions`
        if [[ $? == 0 ]]
        then
            COMPREPLY=( $(compgen -W "${actions}" ${cur}) )
        fi
        _clean
        return 0
    fi

    #  Complete parameters
    if [[ ${__no_opts_cur} > 2 ]]
    then
        local params
        local cur_arg
        
        ((cur_arg=__no_opts_cur-3))
        params=`${COMP_WORDS[@]} --completions ${cur_arg}`
        case "$?" in
            "0")
                COMPREPLY=( $(compgen -W "${params}" ${cur}) )
                ;;
            "1")
                # File completion is requested
                COMPREPLY=( $(compgen -f ${cur}) )
                ;;
            "2")
                # Directory completion is requested
                COMPREPLY=( $(compgen -d ${cur}) )
                ;;
            *)
                ;;
        esac
        _clean
        return 0
    fi

   _clean
   return 0
}

complete -F _cortex_client -o filenames cortex-client