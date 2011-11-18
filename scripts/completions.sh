#!/bin/bash

# Remove ":" from word breaks, otherwise URLs cause problems
COMP_WORDBREAKS=${COMP_WORDBREAKS//:/}

_is_value_option()
{
    local opt="$1"
    local w

    for w in ${__value_options}
    do
        if [[ "${w}" == "${opt}" ]]
        then
            return 1
        fi
    done
    return 0
}

# Filters given arguments list and produces an array containing "no-options"
# (argument prefixed with -) and options.
# Input:
#   COMP_WORDS global array must be defined
#   COMP_CWORD
#   __value_options
# Output:
#   __no_opts global array, __no_opts[0] is the name of the application
#   __no_opts_cur index of word currently completed, -1 if currently completed
#                    word is an option or an option value
_filter_options()
{
    local index_no_opts index_opts cur_index w num_of_elems

    __no_opts_cur=-1
    num_of_elems=${#COMP_WORDS[@]}
    cur_index=0
    index_no_opts=0
    index_opts=0
    while (( cur_index < num_of_elems ))
    do
        w=${COMP_WORDS[${cur_index}]}
        if [[ ${w} != "" ]]
        then
            case "${w}" in
                -*)
                    # Check if value follows
                    _is_value_option ${w}
                    if [[ $? == 1 ]]
                    then
                        local next
                        ((next=cur_index+1))
                        if (( ${next} < ${num_of_elems} ))
                        then
                            if [[ ${COMP_WORDS[${next}]} != -* ]]
                            then
                                # Value follows, skip it
                                ((cur_index++))
                            fi
                        fi
                    fi
                    ;;
                *)
                    __no_opts[${index_no_opts}]=${w}
                    if [[ ${cur_index} == ${COMP_CWORD} ]]
                    then
                        __no_opts_cur=${index_no_opts}
                    fi
                    ((index_no_opts++))
                    ;;
            esac
        fi
        ((cur_index++))
    done
}

_setup()
{
    declare -a __no_opts __no_opts_cur

    __no_opts=()
    __no_opts_cur=-1
    __value_options=$(${COMP_WORDS[0]} --options-with-value)
}

_clean()
{
    unset __no_opts __no_opts_cur
    unset __value_options
    unset __escaped_string
}

_print_debug()
{
    echo "Cortex-options:"
    echo "__value_options" ${__value_options}
    echo "Words:"
    echo ${COMP_WORDS[@]}
    echo ${COMP_CWORD}
    echo "Commands:"
    echo ${__no_opts[@]}
    echo ${__no_opts_cur}
}

# This helper function was written in order to overcome a bash issue with
# string substitutions: when a string contains a non-ASCII character,
# substitution does not work.
_escape_spaces()
{
    __escaped_string=""
    local to_escape=$1
    local string_size=${#to_escape}
    local i=0
    while (( i < string_size ))
    do
        cur_char=${to_escape:$i:1}
        if [[ "${cur_char}" == " " ]]
        then
            __escaped_string=${__escaped_string}"\\ "
        else
            __escaped_string=${__escaped_string}${cur_char}
        fi
        ((i++))
    done
}

_cortex_client()
{
    local cur opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"

    _setup
    _filter_options

    #_print_debug
    #_clean
    #return 0

    #
    #  Cortex-client's options.
    #
    if [[ ${cur} == -* ]]
    then
        local opts=$(${COMP_WORDS[0]} --options)
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    else
        local prev
        prev="${COMP_WORDS[COMP_CWORD-1]}"
        _is_value_option ${prev}
        if [[ $? == 1 ]]
        then
            # TODO : value completion
            return 0
        fi
    fi

    #
    #  Cortex-client's resources and services.
    #
    local resources=`${__no_opts[0]} --resources`

    #  Complete resources
    if [[ ${__no_opts_cur} == 1 || ${#__no_opts[@]} == 1 ]]
    then
        COMPREPLY=( $(compgen -W "${resources}" ${cur}) )
        _clean
        return 0
    fi

    #  Complete action if no argument is yet given
    if [[ ${__no_opts_cur} == 2 || ${#__no_opts[@]} == 2 ]]
    then
        local resource=${__no_opts[1]}
        local actions
        actions=`${COMP_WORDS[0]} ${resource} __available_actions`
        if [[ $? == 0 ]]
        then
            COMPREPLY=( $(compgen -W "${actions}" ${cur}) )
        fi
        _clean
        return 0
    fi

    #  Complete parameters
    if [[ ${__no_opts_cur} > 2  || ${#__no_opts[@]} > 2 ]]
    then
        local params
        local cur_arg

        if [[ ${__no_opts_cur} == -1 ]]
        then
            ((cur_arg=${#__no_opts[@]}-3))
        else
            ((cur_arg=__no_opts_cur-3))
        fi
        params=`${COMP_WORDS[@]} --completions ${cur_arg}`
        case "$?" in
            "0")
                # Ignore spaces when parsing possible values
                local IFS=$'\n'
                COMPREPLY=( $(compgen -W "${params}" -- ${cur}) )

                # Escape spaces
                local cur_comp=0
                local num_of_comps=${#COMPREPLY[@]}
                while ((cur_comp < num_of_comps))
                do
                    local to_escape=${COMPREPLY[$cur_comp]}
                    _escape_spaces $to_escape
                    local escaped=${__escaped_string}
                    COMPREPLY[$cur_comp]=$escaped
                    ((cur_comp++))
                done
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

complete -F _cortex_client cortex-client